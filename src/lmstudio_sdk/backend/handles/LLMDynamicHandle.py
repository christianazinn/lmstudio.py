from typing import Any, Callable, Coroutine, List, Optional, Tuple

import lmstudio_sdk.dataclasses as dc
import lmstudio_sdk.utils as utils
import lmstudio_sdk.backend.communications as comms

from .DynamicHandle import DynamicHandle


logger = utils.get_logger(__name__)


def predict_internal_process_result(extra):
    """Abort handler callback for predict_internal."""
    original_extra = extra.get("extra")
    cancel_event = original_extra.get("cancel_event")
    cancel_send = original_extra.get("cancel_send")
    channel_id = extra.get("channelId")

    cancel_event.subscribeOnce(lambda: cancel_send(channel_id))

    return original_extra


class LLMDynamicHandle(DynamicHandle):
    """Represents a set of requirements for a model.

    It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.

    For example, if you got the model via `client.llm.get({
    "identifier": "my-identifier"})`, you will get a
    `LLMSpecificModel` for the model with the identifier
    `my-identifier`. If the model is unloaded, and another model
    is loaded with the same identifier,
    using the same `LLMSpecificModel` will use the new model.
    """

    _internal_kv_config_stack = dc.KVConfigStack(layers=[])

    def __prediction_config_to_kv_config(
        self, prediction_config: Optional[dc.LLMPredictionConfig]
    ) -> dc.KVConfig:
        """Converts a prediction config to a KVConfig."""
        fields = []
        if prediction_config is not None:
            for default_key in [
                "temperature",
                "context_overflow_policy",
                "stop_strings",
                "structured",
                "top_k_sampling",
            ]:
                if default_key in prediction_config:
                    fields.append(
                        {
                            "key": default_key,
                            "value": prediction_config[default_key],
                        }
                    )
            if "max_predicted_tokens" in prediction_config:
                fields.append(
                    {
                        "key": "max_predicted_tokens",
                        "value": utils.number_to_checkbox_numeric(
                            prediction_config["max_predicted_tokens"], -1, 1
                        ),
                    }
                )
            if "repeat_penalty" in prediction_config:
                fields.append(
                    {
                        "key": "repeat_penalty",
                        "value": utils.number_to_checkbox_numeric(
                            prediction_config["repeat_penalty"], 1, 1
                        ),
                    }
                )
            if "min_p_sampling" in prediction_config:
                fields.append(
                    {
                        "key": "min_p_sampling",
                        "value": utils.number_to_checkbox_numeric(
                            prediction_config["min_p_sampling"], 0, 0.05
                        ),
                    }
                )
            if "top_p_sampling" in prediction_config:
                fields.append(
                    {
                        "key": "top_p_sampling",
                        "value": utils.number_to_checkbox_numeric(
                            prediction_config["top_p_sampling"], 1, 0.95
                        ),
                    }
                )
            if "cpu_threads" in prediction_config:
                fields.append(
                    {
                        "key": "llama.cpu_threads",
                        "value": prediction_config["cpu_threads"],
                    }
                )
        return {"fields": fields}

    def __split_opts(
        self, opts: Optional[dc.LLMPredictionOpts]
    ) -> Tuple[dc.LLMPredictionConfig, dc.LLMPredictionExtraOpts]:
        if opts is None:
            return {}, {}
        extra_opts: dc.LLMPredictionExtraOpts = {}
        for key in ["on_prompt_processing_progress", "on_first_token"]:
            if key in opts:
                extra_opts[key] = opts[key]
                del opts[key]
        return opts, extra_opts

    def __resolve_completion_context(
        self, contextInput: dc.LLMCompletionContextInput
    ) -> dc.LLMContext:
        return {
            "history": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": contextInput}],
                }
            ]
        }

    def __resolve_conversation_context(
        self, context_input: dc.LLMConversationContextInput
    ) -> dc.LLMContext:
        return {
            "history": [
                {
                    "role": item.get("role", "user"),
                    "content": [
                        {"type": "text", "text": item.get("content", "")}
                    ],
                }
                for item in context_input
            ]
        }

    def __predict_internal(
        self,
        model_specifier: dc.ModelSpecifier,
        context: dc.LLMContext,
        prediction_config_stack: dc.KVConfigStack,
        cancel_event: utils.SyncBufferedEvent | utils.AsyncBufferedEvent,
        extra_opts: dc.LLMPredictionExtraOpts,
        on_fragment: Callable[[str], None],
        on_finished: Callable[
            [
                dc.LLMPredictionStats,
                dc.ModelDescriptor,
                dc.KVConfig,
                dc.KVConfig,
            ],
            None,
        ],
        on_error: Callable[[Exception], None],
        postprocess: Callable[[dict], Any],
        extra: Optional[dict] = None,
    ) -> (
        comms.SyncOngoingPrediction
        | Coroutine[Any, Any, comms.AsyncOngoingPrediction]
    ):
        """Internal method for a prediction process.

        Should never be called externally! This is not part of the public API.

        Args:
            model_specifier: The model specifier of the model
                to use for prediction.
            context: The context to use for prediction. Will usually be
                formatted by a public API method.
            prediction_config_stack: The prediction config stack.
            cancel_event: A pending prediction cancel event, to be registered.
                Will be added to the returned ongoing prediction
                and triggerable using `.cancel()`.
            extra_opts: Extra prediction options not in the config stack.
            on_fragment: Callback on receiving a response fragment.
            on_finished: Callback on response completion.
            on_error: Callback on channel error.
            postprocess: The postprocess handler. See `BaseClientPort`.
            extra: Extra data. See `BaseClientPort`.

        Returns:
            The ongoing prediction invoked on the server.

        Raises:
            ChannelError: if an error occurs in the channel during prediction.
        """
        finished = self._port._rpc_complete_event()
        is_first_token = True

        def handle_fragments(message: dict):
            message_type = message.get("type", "")
            if message_type == "fragment":
                on_fragment(message.get("fragment", ""))
                nonlocal is_first_token
                if is_first_token:
                    is_first_token = False
                    logger.debug("First token received.")
                    if "on_first_token" in extra_opts:
                        on_first_token = extra_opts.get("on_first_token")
                        if on_first_token is not None:
                            on_first_token()
            elif message_type == "promptProcessingProgress":
                logger.debug(
                    "Processing prompt, progress: %f",
                    message.get("progress", 0.0),
                )
                if "on_prompt_processing_progress" in extra_opts:
                    on_prompt_processing_progress = extra_opts.get(
                        "on_prompt_processing_progress"
                    )
                    if on_prompt_processing_progress is not None:
                        on_prompt_processing_progress(
                            message.get("progress", 0.0)
                        )
            elif message_type == "success":
                nonlocal finished
                finished.set()
                logger.debug("Prediction completed successfully.")
                on_finished(
                    message.get("stats", {}),
                    message.get("descriptor", {}),
                    message.get("loadConfig", {}),
                    message.get("predictionConfig", {}),
                )
            elif message_type == "channelError":
                logger.error(
                    "Prediction failed: %s",
                    utils.pretty_print_error(message.get("error")),
                )
                on_error(utils.ChannelError(message.get("error").get("title")))

        def cancel_send(channel_id):
            logger.info(
                "Attempting to send cancel message to channel %d.", channel_id
            )
            if not finished.is_set():
                return self._port.send_channel_message(
                    channel_id, {"type": "cancel"}
                )
            # HACK easier to just eat a debug message
            return self._port.send_channel_message(None, None)

        extra = extra or {}
        extra.update(
            {"cancel_event": cancel_event, "cancel_send": cancel_send}
        )

        return self._port.create_channel(
            "predict",
            {
                "modelSpecifier": model_specifier,
                "context": context,
                "predictionConfigStack": prediction_config_stack,
            },
            handle_fragments,
            lambda x: postprocess(predict_internal_process_result(x)),
            extra,
        )

    def complete(
        self,
        prompt: dc.LLMCompletionContextInput,
        opts: Optional[dc.LLMPredictionOpts] = None,
    ) -> (
        comms.SyncOngoingPrediction
        | Coroutine[Any, Any, comms.AsyncOngoingPrediction]
    ):
        """
        Use the loaded model to predict text.

        This method returns an OngoingPrediction object,
        sync or async depending on the client context.
        It can be used as a "promise" if you only care about the final result
        or as an (async) iterable if you want to stream the results as they
        are generated.

        Example synchronous usage as a promise (Resolves to a `PredictionResult`):

        ```python
        result = model.complete("When will The Winds of Winter be released?")
        print(result.result().content)
        ```

        And asynchronous:

        ```python
        result = await model.complete("When will The Winds of Winter be released?")
        print((await result).content)
        ```

        Example usage as sync iterable (streaming):

        ```python
        completion = model.complete("When will The Winds of Winter be released?")

        for (fragment of completion):
            print(fragment, end='')
        ```

        And asynchronous:

        ```python
        completion = await model.complete("When will The Winds of Winter be released?")
        async for fragment in completion:
            print(fragment, end='')
        ```

        The result is already available in the internal buffer after streaming,
        so calling `result()` (e.g. to get prediction stats) will not block.

        The OngoingPrediction object can also be used to cancel the prediction
        using `cancel()`.

        Args:
            prompt: The prompt to use for generating a completion.
            opts: Options for the prediction, if any. Defaults to using the
                options set in the LM Studio server.

        Returns:
            An OngoingPrediction object representing the prediction process.
        """
        utils._assert(
            isinstance(prompt, str),
            "complete: prompt must be a string, got %s",
            type(prompt),
            logger,
        )

        config, extra_opts = self.__split_opts(opts)

        if self._port.is_async():
            OngoingPrediction = comms.AsyncOngoingPrediction
            BufferedEvent = utils.AsyncBufferedEvent
        else:
            OngoingPrediction = comms.SyncOngoingPrediction
            BufferedEvent = utils.SyncBufferedEvent

        cancel_event, emit_cancel_event = BufferedEvent.create()
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(
            emit_cancel_event
        )

        config["stop_strings"] = []
        prediction_layers = self._internal_kv_config_stack.get("layers", [])
        prediction_layers.append(
            dc.KVConfigStackLayer(
                layerName=dc.KVConfigLayerName.API_OVERRIDE,
                config=self.__prediction_config_to_kv_config(config),
            )
        )
        prediction_layers.append(
            {
                "layerName": dc.KVConfigLayerName.COMPLETE_MODE_FORMATTING,
                "config": dc.convert_dict_to_kv_config(
                    {
                        "promptTemplate": {
                            "type": "jinja",
                            "jinjaPromptTemplate": {
                                "bosToken": "",
                                "eosToken": "",
                                "template": "{% for message in messages %}{{ message['content'] }}{% endfor %}",
                            },
                            "stop_strings": [],
                        }
                    }
                ),
            }
        )

        return self.__predict_internal(
            self._specifier,
            self.__resolve_completion_context(prompt),
            {"layers": prediction_layers},
            cancel_event,
            extra_opts,
            lambda fragment: push(fragment),
            lambda stats,
            model_info,
            load_model_config,
            prediction_config: finished(
                stats, model_info, load_model_config, prediction_config
            ),
            lambda error: failed(error),
            lambda x: x.get("ongoing_prediction"),
            extra={"ongoing_prediction": ongoing_prediction},
        )

    def respond(
        self,
        history: dc.LLMConversationContextInput,
        opts: Optional[dc.LLMPredictionOpts] = None,
    ) -> (
        comms.SyncOngoingPrediction
        | Coroutine[Any, Any, comms.AsyncOngoingPrediction]
    ):
        """
        Use the loaded model to generate a response based on the given history.

        This method returns an OngoingPrediction object,
        sync or async depending on the client context.
        It can be used as a "promise" if you only care about the final result
        or as an (async) iterable if you want to stream the results as they
        are generated.

        If you are tracking a conversation, you should modify the chat `history`
        within your application; whatever is sent to this method will be used
        in the prediction! This method does not store any conversation state.
        For instance, if you are creating a chat UI, simply modifying an entry
        in the `history` list will update the conversation as if the user
        edited a message.

        Example synchronous usage as a promise (Resolves to a `PredictionResult`):

        ```python
        result = model.respond([{
            "role": "user",
            "content": "When will The Winds of Winter be released?"
        }])
        print(result.result().content)
        ```

        And asynchronous:

        ```python
        result = await model.respond([{
            "role": "user",
            "content": "When will The Winds of Winter be released?"
        }])
        print((await result).content)
        ```

        Example usage as sync iterable (streaming):

        ```python
        completion = model.respond([{
            "role": "user",
            "content": "When will The Winds of Winter be released?"
        }])

        for (fragment of completion):
            print(fragment, end='')
        ```

        And asynchronous:

        ```python
        completion = await model.respond([{
            "role": "user",
            "content": "When will The Winds of Winter be released?"
        }])
        async for fragment in completion:
            print(fragment, end='')
        ```

        The result is already available in the internal buffer after streaming,
        so calling `result()` (e.g. to get prediction stats) will not block.

        The OngoingPrediction object can also be used to cancel the prediction
        using `cancel()`.

        Args:
            history: The chat history to use for generating a completion.
            opts: Options for the prediction, if any. Defaults to using the
                options set in the LM Studio server.

        Returns:
            An OngoingPrediction object representing the prediction process.
        """
        try:
            resolved_context = self.__resolve_conversation_context(history)
        except Exception as e:
            logger.error("Failed to resolve conversation context: %s", str(e))
            raise ValueError(
                "History must be a list conforming to \
                LLMConversationContextInput, got something else."
            )
        return self.predict(resolved_context, opts)

    def unstable_get_context_length(self) -> utils.LiteralOrCoroutine[int]:
        """Get the context length of the model.

        Returns:
            The context length of the model.
        """
        return self.get_load_config(
            postprocess=lambda x: dc.find_key_in_kv_config(
                x, "llm.load.contextLength"
            )
            or -1
        )

    def unstable_apply_prompt_template(
        self,
        context: dc.LLMContext,
        opts: Optional[dc.LLMApplyPromptTemplateOpts] = None,
    ) -> utils.LiteralOrCoroutine[str]:
        """Apply a prompt template to the given context.

        Args:
            context: The context to apply the prompt template to.
            opts: Options for applying the prompt template, if any.

        Returns:
            The formatted prompt template.
        """
        return self._port.call_rpc(
            "applyPromptTemplate",
            {
                "specifier": self._specifier,
                "context": context,
                "opts": opts,
                "predictionConfigStack": self._internal_kv_config_stack,
            },
            lambda x: x.get("formatted", ""),
        )

    def unstable_tokenize(
        self, input_string: str
    ) -> utils.LiteralOrCoroutine[List[int]]:
        """Tokenize the input string.

        Always tokenize using the exact model you will be using
        for prediction, as tokenization can vary between models.

        Args:
            input_string: The string to tokenize.

        Returns:
            A list of integers representing the tokenized string.
        """
        utils._assert(
            isinstance(input_string, str),
            "unstable_tokenize: input_string must be a string, got %s",
            type(input_string),
            logger,
        )
        return self._port.call_rpc(
            "tokenize",
            {"specifier": self._specifier, "inputString": input_string},
            lambda x: x.get("tokens", [-1]),
        )

    def unstable_count_tokens(
        self, input_string: str
    ) -> utils.LiteralOrCoroutine[int]:
        """Count the number of tokens in the input string.

        Args:
            input_string: The string to count the tokens of.

        Returns:
            The number of tokens in the input string.
        """
        utils._assert(
            isinstance(input_string, str),
            "unstable_count_tokens: input_string must be a string, got %s",
            type(input_string),
            logger,
        )
        return self._port.call_rpc(
            "countTokens",
            {"specifier": self._specifier, "inputString": input_string},
            lambda x: x.get("tokenCount", -1),
        )

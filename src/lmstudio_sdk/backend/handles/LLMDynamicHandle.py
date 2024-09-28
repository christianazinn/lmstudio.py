from typing import Any, Callable, List, Tuple
from functools import partial

from ...dataclasses import (
    convert_dict_to_kv_config,
    find_key_in_kv_config,
    KVConfig,
    KVConfigLayerName,
    KVConfigStack,
    KVConfigStackLayer,
    LLMApplyPromptTemplateOpts,
    LLMCompletionContextInput,
    LLMContext,
    LLMConversationContextInput,
    LLMPredictionConfig,
    LLMPredictionExtraOpts,
    LLMPredictionOpts,
    LLMPredictionStats,
    ModelDescriptor,
    ModelSpecifier,
)
from ...utils import (
    BufferedEvent,
    ChannelError,
    get_logger,
    LiteralOrCoroutine,
    number_to_checkbox_numeric,
    pretty_print_error,
)
from ..communications import BaseOngoingPrediction
from .DynamicHandle import DynamicHandle


logger = get_logger(__name__)


def predict_internal_process_result(extra):
    original_extra = extra.get("extra")
    cancel_event = original_extra.get("cancel_event")
    cancel_send = original_extra.get("cancel_send")
    channel_id = extra.get("channelId")

    cancel_event.subscribeOnce(partial(cancel_send, channel_id))

    return original_extra


class LLMDynamicHandle(DynamicHandle):
    """
    This represents a set of requirements for a model. It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.

    For example, if you got the model via `client.llm.get("my-identifier")`, you will get a
    `LLMModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
    another model is loaded with the same identifier, using the same `LLMModel` will use the new
    model.

    :public:
    """

    _internal_kv_config_stack = KVConfigStack(layers=[])

    def prediction_config_to_kv_config(self, prediction_config: LLMPredictionConfig | None) -> KVConfig:
        fields = []
        if prediction_config is not None:
            # HACK i hate this
            for default_key in [
                "temperature",
                "context_overflow_policy",
                "stop_strings",
                "structured",
                "top_k_sampling",
            ]:
                if default_key in prediction_config:
                    fields.append({"key": default_key, "value": prediction_config[default_key]})
            if "max_predicted_tokens" in prediction_config:
                fields.append(
                    {
                        "key": "max_predicted_tokens",
                        "value": number_to_checkbox_numeric(prediction_config["max_predicted_tokens"], -1, 1),
                    }
                )
            if "repeat_penalty" in prediction_config:
                fields.append(
                    {
                        "key": "repeat_penalty",
                        "value": number_to_checkbox_numeric(prediction_config["repeat_penalty"], 1, 1),
                    }
                )
            if "min_p_sampling" in prediction_config:
                fields.append(
                    {
                        "key": "min_p_sampling",
                        "value": number_to_checkbox_numeric(prediction_config["min_p_sampling"], 0, 0.05),
                    }
                )
            if "top_p_sampling" in prediction_config:
                fields.append(
                    {
                        "key": "top_p_sampling",
                        "value": number_to_checkbox_numeric(prediction_config["top_p_sampling"], 1, 0.95),
                    }
                )
            if "cpu_threads" in prediction_config:
                fields.append({"key": "llama.cpu_threads", "value": prediction_config["cpu_threads"]})
        return {"fields": fields}

    def split_opts(self, opts: LLMPredictionOpts) -> Tuple[LLMPredictionConfig, LLMPredictionExtraOpts]:
        extra_opts: LLMPredictionExtraOpts = {}
        for key in ["on_prompt_processing_progress", "on_first_token"]:
            if key in opts:
                extra_opts[key] = opts[key]
                del opts[key]
        return opts, extra_opts

    def _resolve_completion_context(self, contextInput: LLMCompletionContextInput) -> LLMContext:
        return {"history": [{"role": "user", "content": [{"type": "text", "text": contextInput}]}]}

    def _resolve_conversation_context(self, context_input: LLMConversationContextInput) -> LLMContext:
        return {
            "history": [
                {"role": item.get("role", "user"), "content": [{"type": "text", "text": item.get("content", "")}]}
                for item in context_input
            ]
        }

    def _predict_internal(
        self,
        model_specifier: ModelSpecifier,
        context: LLMContext,
        prediction_config_stack: KVConfigStack,
        cancel_event: BufferedEvent,
        extra_opts: LLMPredictionExtraOpts,
        on_fragment: Callable[[str], None],
        on_finished: Callable[[LLMPredictionStats, ModelDescriptor, KVConfig, KVConfig], None],
        on_error: Callable[[Exception], None],
        postprocess: Callable[[dict], Any],
        extra: dict | None = None,
    ) -> LiteralOrCoroutine[BaseOngoingPrediction]:
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
                logger.debug(f"Processing prompt, progress: {message.get('progress', 0.0)}")
                if "on_prompt_processing_progress" in extra_opts:
                    on_prompt_processing_progress = extra_opts.get("on_prompt_processing_progress")
                    if on_prompt_processing_progress is not None:
                        on_prompt_processing_progress(message.get("progress", 0.0))
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
                logger.error(f"Prediction failed: {pretty_print_error(message.get('error'))}")
                on_error(ChannelError(message.get("error").get("title")))

        def cancel_send(channel_id):
            logger.info(f"Attempting to send cancel message to channel {channel_id}.")
            if not finished.is_set():
                return self._port.send_channel_message(channel_id, {"type": "cancel"})
            # HACK side effect of the decorator, easier to just eat an extra debug message
            return self._port.send_channel_message(None, None)

        extra = extra or {}
        extra.update({"cancel_event": cancel_event, "cancel_send": cancel_send})

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
        self, prompt: LLMCompletionContextInput, opts: LLMPredictionOpts
    ) -> LiteralOrCoroutine[BaseOngoingPrediction]:
        """
        Use the loaded model to predict text.

        This method returns an {@link OngoingPrediction} object. An ongoing prediction can be used as a
        promise (if you only care about the final result) or as an async iterable (if you want to
        stream the results as they are being generated).

        Example usage as a promise (Resolves to a {@link PredictionResult}):

        ```typescript
        const result = await model.complete("When will The Winds of Winter be released?");
        console.log(result.content);
        ```

        Or

        ```typescript
        model.complete("When will The Winds of Winter be released?")
         .then(result => console.log(result.content))
         .catch(error => console.error(error));
        ```

        Example usage as an async iterable (streaming):

        ```typescript
        for await (const fragment of model.complete("When will The Winds of Winter be released?")) {
          process.stdout.write(fragment);
        }
        ```

        If you wish to stream the result, but also getting the final prediction results (for example,
        you wish to get the prediction stats), you can use the following pattern:

        ```typescript
        const prediction = model.complete("When will The Winds of Winter be released?");
        for await (const fragment of prediction) {
          process.stdout.write(fragment);
        }
        const result = await prediction;
        console.log(result.stats);
        ```

        :param prompt: The prompt to use for prediction.
        :param opts: Options for the prediction.
        """
        config, extra_opts = self.split_opts(opts)

        cancel_event, emit_cancel_event = BufferedEvent.create()
        if self._port.is_async():
            from ..communications import AsyncOngoingPrediction as OngoingPrediction
        else:
            from ..communications import OngoingPrediction
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(emit_cancel_event)

        config["stop_strings"] = []
        prediction_layers = self._internal_kv_config_stack.get("layers", [])
        prediction_layers.append(
            {"layerName": KVConfigLayerName.API_OVERRIDE, "config": self.prediction_config_to_kv_config(config)}
        )
        prediction_layers.append(
            {
                "layerName": KVConfigLayerName.COMPLETE_MODE_FORMATTING,
                "config": convert_dict_to_kv_config(
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

        return self._predict_internal(
            self._specifier,
            self._resolve_completion_context(prompt),
            {"layers": prediction_layers},
            cancel_event,
            extra_opts,
            lambda fragment: push(fragment),
            lambda stats, model_info, load_model_config, prediction_config: finished(
                stats, model_info, load_model_config, prediction_config
            ),
            lambda error: failed(error),
            lambda x: x.get("ongoing_prediction"),
            extra={"ongoing_prediction": ongoing_prediction},
        )

    def respond(
        self, history: LLMConversationContextInput, opts: LLMPredictionOpts
    ) -> LiteralOrCoroutine[BaseOngoingPrediction]:
        """
        Use the loaded model to generate a response based on the given history.

        This method returns an {@link OngoingPrediction} object. An ongoing prediction can be used as a
        promise (if you only care about the final result) or as an async iterable (if you want to
        stream the results as they are being generated).

        Example usage as a promise (Resolves to a {@link PredictionResult}):

        ```typescript
        const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
        const result = await model.respond(history);
        console.log(result.content);
        ```

        Or

        ```typescript
        const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
        model.respond(history)
         .then(result => console.log(result.content))
         .catch(error => console.error(error));
        ```

        Example usage as an async iterable (streaming):

        ```typescript
        const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
        for await (const fragment of model.respond(history)) {
          process.stdout.write(fragment);
        }
        ```

        If you wish to stream the result, but also getting the final prediction results (for example,
        you wish to get the prediction stats), you can use the following pattern:

        ```typescript
        const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
        const prediction = model.respond(history);
        for await (const fragment of prediction) {
          process.stdout.write(fragment);
        }
        const result = await prediction;
        console.log(result.stats);
        ```

        :param history: The LLMChatHistory array to use for generating a response.
        :param opts: Options for the prediction.
        """
        return self.predict(self._resolve_conversation_context(history), opts)

    def predict(self, context: LLMContext, opts: LLMPredictionOpts) -> LiteralOrCoroutine[BaseOngoingPrediction]:
        config, extra_opts = self.split_opts(opts)

        cancel_event, emit_cancel_event = BufferedEvent.create()
        if self._port.is_async():
            from ..communications import AsyncOngoingPrediction as OngoingPrediction
        else:
            from ..communications import OngoingPrediction
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(emit_cancel_event)

        api_override_layer = KVConfigStackLayer(
            layerName=KVConfigLayerName.API_OVERRIDE, config=self.prediction_config_to_kv_config(config)
        )
        prediction_layers = self._internal_kv_config_stack.get("layers", [])
        prediction_layers.append(api_override_layer)

        return self._predict_internal(
            self._specifier,
            context,
            {"layers": prediction_layers},
            cancel_event,
            extra_opts,
            lambda fragment: push(fragment),
            lambda stats, model_info, load_model_config, prediction_config: finished(
                stats, model_info, load_model_config, prediction_config
            ),
            lambda error: failed(error),
            lambda x: x.get("ongoing_prediction"),
            extra={"ongoing_prediction": ongoing_prediction},
        )

    def unstable_get_context_length(self) -> LiteralOrCoroutine[int]:
        return self.get_load_config(postprocess=lambda x: find_key_in_kv_config(x, "llm.load.contextLength") or -1)

    def unstable_apply_prompt_template(
        self, context: LLMContext, opts: LLMApplyPromptTemplateOpts | None = None
    ) -> LiteralOrCoroutine[str]:
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

    def unstable_tokenize(self, input_string: str) -> LiteralOrCoroutine[List[int]]:
        if not isinstance(input_string, str):
            logger.error(f"unstable_tokenize: input_string must be a string, got {type(input_string)}")
            raise ValueError("Input string must be a string.")
        return self._port.call_rpc(
            "tokenize", {"specifier": self._specifier, "inputString": input_string}, lambda x: x.get("tokens", [-1])
        )

    def unstable_count_tokens(self, input_string: str) -> LiteralOrCoroutine[int]:
        if not isinstance(input_string, str):
            logger.error(f"unstable_count_tokens: input_string must be a string, got {type(input_string)}")
            raise ValueError("Input string must be a string.")
        return self._port.call_rpc(
            "countTokens",
            {"specifier": self._specifier, "inputString": input_string},
            lambda x: x.get("tokenCount", -1),
        )

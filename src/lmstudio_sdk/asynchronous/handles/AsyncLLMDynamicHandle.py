from typing import List, Callable

from ...common import (
    BaseLLMDynamicHandle,
    BufferedEvent,
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
    LLMPredictionExtraOpts,
    LLMPredictionOpts,
    LLMPredictionStats,
    ModelDescriptor,
    ModelSpecifier,
)
from .AsyncDynamicHandle import DynamicHandle
from ..communications import OngoingPrediction


class LLMDynamicHandle(DynamicHandle, BaseLLMDynamicHandle):
    """
    This represents a set of requirements for a model. It is not tied to a specific model, but rather
    to a set of requirements that a model must satisfy.

    For example, if you got the model via `client.llm.get("my-identifier")`, you will get a
    `LLMModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
    another model is loaded with the same identifier, using the same `LLMModel` will use the new
    model.

    :public:
    """

    async def __predict_internal(
        self,
        modelSpecifier: ModelSpecifier,
        context: LLMContext,
        predictionConfigStack: KVConfigStack,
        cancel_event: BufferedEvent,
        extraOpts: LLMPredictionExtraOpts,
        on_fragment: Callable[[str], None],
        on_finished: Callable[[LLMPredictionStats, ModelDescriptor, KVConfig, KVConfig], None],
        on_error: Callable[[Exception], None],
    ):
        finished = False

        async def handle_fragments(message: dict):
            message_type = message.get("type", "")
            if message_type == "fragment":
                on_fragment(message.get("fragment", ""))
                if "on_first_token" in extraOpts:
                    on_first_token = extraOpts.get("on_first_token")
                    if on_first_token is not None:
                        on_first_token()
            elif message_type == "promptProcessingProgress":
                if "on_prompt_processing_progress" in extraOpts:
                    on_prompt_processing_progress = extraOpts.get("on_prompt_processing_progress")
                    if on_prompt_processing_progress is not None:
                        on_prompt_processing_progress(message.get("progress", 0.0))
            elif message_type == "success":
                nonlocal finished
                finished = True
                on_finished(
                    message.get("stats", {}),
                    message.get("descriptor", {}),
                    message.get("loadConfig", {}),
                    message.get("predictionConfig", {}),
                )
            # FIXME this probably doesn't work
            elif message_type == "error":
                on_error(Exception(message.get("message", "Unknown error")))

        print("about to create channel")

        channel_id = await self._port.create_channel(
            "predict",
            {
                "modelSpecifier": modelSpecifier,
                "context": context,
                "predictionConfigStack": predictionConfigStack,
            },
            handle_fragments,
        )

        print("channel nominal")

        def cancel_send():
            if not finished:
                self._port.send_channel_message(channel_id, {"type": "cancel"})

        cancel_event.subscribeOnce(cancel_send)

    async def complete(self, prompt: LLMCompletionContextInput, opts: LLMPredictionOpts) -> OngoingPrediction:
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

        await self.__predict_internal(
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
        )
        return ongoing_prediction

    async def respond(self, history: LLMConversationContextInput, opts: LLMPredictionOpts) -> OngoingPrediction:
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
        return await self.predict(self._resolve_conversation_context(history), opts)

    async def predict(self, context: LLMContext, opts: LLMPredictionOpts) -> OngoingPrediction:
        """
        :alpha:
        """

        config, extra_opts = self.split_opts(opts)

        cancel_event, emit_cancel_event = BufferedEvent.create()
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(emit_cancel_event)

        api_override_layer = KVConfigStackLayer(
            layerName=KVConfigLayerName.API_OVERRIDE, config=self.prediction_config_to_kv_config(config)
        )
        prediction_layers = self._internal_kv_config_stack.get("layers", [])
        prediction_layers.append(api_override_layer)

        print(self._specifier)
        print(context)
        print(prediction_layers)

        await self.__predict_internal(
            self._specifier,
            context,
            KVConfigStack(layers=prediction_layers),
            cancel_event,
            extra_opts,
            lambda fragment: push(fragment),
            lambda stats, model_info, load_model_config, prediction_config: finished(
                stats, model_info, load_model_config, prediction_config
            ),
            lambda error: failed(error),
        )
        return ongoing_prediction

    async def unstable_get_context_length(self) -> int:
        context_length = find_key_in_kv_config(await self.get_load_config(), "contextLength")
        return context_length if context_length else -1

    async def unstable_apply_prompt_template(
        self, context: LLMContext, opts: LLMApplyPromptTemplateOpts | None = None
    ) -> str:
        return (
            await self._port.call_rpc(
                "applyPromptTemplate",
                {
                    "specifier": self._specifier,
                    "context": context,
                    "opts": opts,
                    "predictionConfigStack": self._internal_kv_config_stack,
                },
            )
        ).get("formatted", "")

    async def unstable_tokenize(self, input_string: str) -> List[int]:
        return (await self._port.call_rpc("tokenize", {"specifier": self._specifier, "inputString": input_string})).get(
            "tokens", [-1]
        )

    async def unstable_count_tokens(self, input_string: str) -> int:
        return (
            await self._port.call_rpc("countTokens", {"specifier": self._specifier, "inputString": input_string})
        ).get("tokenCount", -1)

from typing import List, Callable, Optional, Dict, Union, Tuple

from TypesAndInterfaces.relevant.DynamicHandles.DynamicHandle import DynamicHandle
from TypesAndInterfaces.relevant.Predictions.OngoingPrediction import OngoingPrediction
from TypesAndInterfaces.relevant.Predictions.LLMPredictionOpts import (
    LLMPredictionOpts,
    LLMPredictionConfig,
    LLMPredictionExtraOpts,
)
from TypesAndInterfaces.relevant.LLMGeneralSettings.LLMChatHistory import (
    LLMConversationContextInput,
    LLMCompletionContextInput,
    LLMContext,
)
from TypesAndInterfaces.relevant.LLMGeneralSettings.LLMApplyPromptTemplateOpts import LLMApplyPromptTemplateOpts
from TypesAndInterfaces.relevant.Predictions.LLMPredictionStats import LLMPredictionStats
from TypesAndInterfaces.relevant.ModelDescriptors.ModelDescriptor import ModelDescriptor
from TypesAndInterfaces.relevant.ModelDescriptors.ModelSpecifier import ModelSpecifier
from TypesAndInterfaces.relevant.LLMGeneralSettings.KVConfig import (
    KVConfig,
    KVConfigStack,
    KVConfigStackLayer,
    KVConfigLayerName,
    convert_dict_to_kv_config,
    find_key_in_kv_config
)
from TypesAndInterfaces.relevant.Defaults.BufferedEvent import BufferedEvent


def number_to_checkbox_numeric(
    value: Optional[float], unchecked_value: float, value_when_unchecked: float
) -> Optional[Dict[str, Union[bool, float]]]:
    if value is None:
        return None
    if value == unchecked_value:
        return {"checked": False, "value": value_when_unchecked}
    if value != unchecked_value:
        return {"checked": True, "value": value}


def prediction_config_to_kv_config(prediction_config: LLMPredictionConfig | None) -> KVConfig:
    fields = []
    if prediction_config is not None:
        # HACK i hate this
        for default_key in ["temperature", "contextOverflowPolicy", "stopStrings", "structured", "topKSampling"]:
            if default_key in prediction_config:
                fields.append({"key": default_key, "value": prediction_config[default_key]})
        if "maxPredictedTokens" in prediction_config:
            fields.append(
                {
                    "key": "maxPredictedTokens",
                    "value": number_to_checkbox_numeric(prediction_config["maxPredictedTokens"], -1, 1),
                }
            )
        if "repeatPenalty" in prediction_config:
            fields.append(
                {"key": "repeatPenalty", "value": number_to_checkbox_numeric(prediction_config["repeatPenalty"], 1, 1)}
            )
        if "minPSampling" in prediction_config:
            fields.append(
                {"key": "minPSampling", "value": number_to_checkbox_numeric(prediction_config["minPSampling"], 0, 0.05)}
            )
        if "topPSampling" in prediction_config:
            fields.append(
                {"key": "topPSampling", "value": number_to_checkbox_numeric(prediction_config["topPSampling"], 1, 0.95)}
            )
        if "cpuThreads" in prediction_config:
            fields.append({"key": "llama.cpuThreads", "value": prediction_config["cpuThreads"]})
    return {"fields": fields}


def split_opts(opts: LLMPredictionOpts) -> Tuple[LLMPredictionConfig, LLMPredictionExtraOpts]:
    extra_opts: LLMPredictionExtraOpts = {}
    for key in ["on_prompt_processing_progress", "on_first_token"]:
        if key in opts:
            extra_opts[key] = opts[key]
            del opts[key]
    return opts, extra_opts


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

    __internal_kv_config_stack = KVConfigStack(layers=[])

    # TODO: un-async this
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
        # TODO ModelSpecifier validation
        finished = False

        async def handle_fragments(message: dict):
            message_type = message.get("type", "")
            print(message_type)
            if message_type == "fragment":
                on_fragment(message.get("fragment", ""))
                if "on_first_token" in extraOpts:
                    extraOpts["on_first_token"]()
            elif message_type == "promptProcessingProgress":
                if "on_prompt_processing_progress" in extraOpts:
                    extraOpts["on_prompt_processing_progress"](message.get("progress", 0.0))
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

        channel_id = await self.port.create_channel(
            "predict",
            {
                "modelSpecifier": modelSpecifier,
                "context": context,
                "predictionConfigStack": predictionConfigStack,
            },
            handle_fragments,
        )

        def cancel_send():
            if not finished:
                # TODO syncify this
                self.port.send_channel_message(channel_id, {"type": "cancel"})

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
        config, extra_opts = split_opts(opts)

        cancel_event, emit_cancel_event = BufferedEvent.create()
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(emit_cancel_event)

        config["stopStrings"] = []
        prediction_layers = self.__internal_kv_config_stack.get("layers", [])
        prediction_layers.append({"layerName": KVConfigLayerName.API_OVERRIDE, "config": prediction_config_to_kv_config(config)})
        prediction_layers.append({
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
                        "stopStrings": [],
                    }
                }
            ),
        })

        # TODO un-async me
        await self.__predict_internal(
            self.specifier,
            self.__resolve_completion_context(prompt),
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

    def __resolve_completion_context(self, contextInput: LLMCompletionContextInput) -> LLMContext:
        return {"history": [{"role": "user", "content": [{"type": "text", "text": contextInput}]}]}

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
        # TODO un-async me
        return await self.predict(self.__resolve_conversation_context(history), opts)

    def __resolve_conversation_context(self, context_input: LLMConversationContextInput) -> LLMContext:
        return {
            "history": [
                {"role": item.get("role", "user"), "content": [{"type": "text", "text": item.get("content", "")}]}
                for item in context_input
            ]
        }

    # TODO: un-async this
    async def predict(self, context: LLMContext, opts: LLMPredictionOpts) -> OngoingPrediction:
        """
        :alpha:
        """

        config, extra_opts = split_opts(opts)

        cancel_event, emit_cancel_event = BufferedEvent.create()
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(emit_cancel_event)

        api_override_layer = KVConfigStackLayer(layerName=KVConfigLayerName.API_OVERRIDE, config=prediction_config_to_kv_config(config))
        prediction_layers = self.__internal_kv_config_stack.get("layers", [])
        prediction_layers.append(api_override_layer)

        # TODO un-async me
        await self.__predict_internal(
            self.specifier,
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

    # TODO: should these be get or something else?
    async def unstable_apply_prompt_template(
        self, context: LLMContext, opts: LLMApplyPromptTemplateOpts | None = None
    ) -> str:
        return (
            await self.port.call_rpc(
                "applyPromptTemplate",
                {
                    "specifier": self.specifier,
                    "context": context,
                    "opts": opts,
                    "predictionConfigStack": self.__internal_kv_config_stack,
                },
            )
        ).get("formatted", "")

    async def unstable_tokenize(self, input_string: str) -> List[int]:
        return (await self.port.call_rpc("tokenize", {"specifier": self.specifier, "inputString": input_string})).get(
            "tokens", [-1]
        )

    async def unstable_count_tokens(self, input_string: str) -> int:
        return (
            await self.port.call_rpc("countTokens", {"specifier": self.specifier, "inputString": input_string})
        ).get("tokenCount", -1)

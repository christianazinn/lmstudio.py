from typing import List, Callable, Optional, Dict, Union
from threading import Lock

from DynamicHandles.DynamicHandle import DynamicHandle
from Predictions.OngoingPrediction import OngoingPrediction
from Predictions.LLMPredictionOpts import LLMPredictionOpts, LLMPredictionConfig
from LLMGeneralSettings.LLMChatHistory import LLMConversationContextInput, LLMCompletionContextInput, LLMContext
from LLMGeneralSettings.LLMApplyPromptTemplateOpts import LLMApplyPromptTemplateOpts
from Predictions.LLMPredictionStats import LLMPredictionStats
from ModelDescriptors.ModelDescriptor import ModelDescriptor
from ModelDescriptors.ModelSpecifier import ModelSpecifier
from LLMGeneralSettings.KVConfig import KVConfig, KVConfigStack


# HACK
class BufferedEvent:
    def __init__(self):
        self.subscribers: List[Callable[[], None]] = []
        self.lock = Lock()

    def subscribeOnce(self, callback: Callable[[], None]):
        with self.lock:
            self.subscribers.append(callback)

    def emit(self):
        with self.lock:
            for subscriber in self.subscribers:
                subscriber()
            self.subscribers.clear()

    @staticmethod
    def create():
        event = BufferedEvent()
        return event, event.emit


def number_to_checkbox_numeric(
    value: Optional[float], unchecked_value: float, value_when_unchecked: float
) -> Optional[Dict[str, Union[bool, float]]]:
    if value is None:
        return None
    if value == unchecked_value:
        return {"checked": False, "value": value_when_unchecked}
    if value != unchecked_value:
        return {"checked": True, "value": value}


def prediction_config_to_kv_config(prediction_config: LLMPredictionConfig) -> KVConfig:
    prediction_config = LLMPredictionConfig.model_validate(prediction_config)
    # TODO maybe revisit when you convert naming conventions to Python
    return KVConfig.convert_dict_to_kv_config(
        {
            "temperature": prediction_config.temperature,
            "contextOverflowPolicy": prediction_config.contextOverflowPolicy,
            "maxPredictedTokens": number_to_checkbox_numeric(prediction_config.maxPredictedTokens, -1, 1),
            "stopStrings": prediction_config.stopStrings,
            "structured": prediction_config.structured,
            "topKSampling": prediction_config.topKSampling,
            "repeatPenalty": number_to_checkbox_numeric(prediction_config.repeatPenalty, 1, 1, 1),
            "minPSampling": number_to_checkbox_numeric(prediction_config.minPSampling, 0, 0.05),
            "topPSampling": number_to_checkbox_numeric(prediction_config.topPSampling, 1, 0.95),
            "llama.cpuThreads": prediction_config.cpuThreads,
        }
    )


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

    __internal_kv_config_stack: KVConfigStack = {"layers": []}

    def __predict_internal(
        self,
        modelSpecifier: ModelSpecifier,
        context: LLMContext,
        predictionConfigStack: KVConfigStack,
        cancel_event: BufferedEvent,
        extraOpts: LLMPredictionOpts | None,
        on_fragment: Callable[[str], None],
        on_finished: Callable[[LLMPredictionStats, ModelDescriptor, KVConfig, KVConfig], None],
        on_error: Callable[[Exception], None],
    ):
        assert isinstance(modelSpecifier, ModelSpecifier)
        context = LLMContext.model_validate(context)
        predictionConfigStack = KVConfigStack.model_validate(predictionConfigStack)
        extraOpts = LLMPredictionOpts.model_validate(extraOpts) if extraOpts is not None else None
        finished = False

        async def handle_fragments(message: dict):
            message_type = message.get("type", "")
            if message_type == "fragment":
                if on_fragment is not None:
                    on_fragment(message.get("fragment", ""))
                if extraOpts is not None and extraOpts.on_first_token is not None:
                    extraOpts.on_first_token()
            elif message_type == "promptProcessingProgress":
                if extraOpts is not None and extraOpts.on_prompt_processing_progress is not None:
                    extraOpts.on_prompt_processing_progress(message.get("progress", 0.0))
            elif message_type == "finished":
                nonlocal finished
                finished = True
                if on_finished is not None:
                    on_finished(
                        LLMPredictionStats.model_validate(message.get("stats", {})),
                        ModelDescriptor.model_validate(message.get("descriptor", {})),
                        KVConfig.model_validate(message.get("loadConfig", {})),
                        KVConfig.model_validate(message.get("predictionConfig", {})),
                    )
            # FIXME this probably doesn't work
            elif message_type == "error":
                if on_error is not None:
                    on_error(Exception(message.get("message", "Unknown error")))

        channel_id = self.port.create_channel(
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
                self.port.send_channel_message(channel_id, {"type": "cancel"})

        cancel_event.subscribe_once(cancel_send)

    def complete(self, prompt: LLMCompletionContextInput, opts: LLMPredictionOpts | None = None) -> OngoingPrediction:
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
        prompt = LLMCompletionContextInput.model_validate(prompt)
        opts = LLMPredictionOpts.model_validate(opts) if opts is not None else None

        # TODO splitOpts
        extra_opts = opts

        cancel_event, emit_cancel_event = BufferedEvent.create()
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(emit_cancel_event)

        extra_opts.set("stopStrings", [])
        api_override_layer = {"layerName": "apiOverride", "config": prediction_config_to_kv_config(extra_opts)}
        complete_mode_formatting_layer = {
            "layerName": "completeModeFormatting",
            "config": KVConfig.convert_dict_to_kv_config(
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
        }
        prediction_layers = self.__internal_kv_config_stack.get("layers", [])
        prediction_layers.append(api_override_layer)
        prediction_layers.append(complete_mode_formatting_layer)

        self.__predict_internal(
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

    def respond(self, history: LLMConversationContextInput, opts: LLMPredictionOpts | None = None) -> OngoingPrediction:
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
        history = LLMConversationContextInput.model_validate(history)
        opts = LLMPredictionOpts.model_validate(opts) if opts is not None else None
        return self.predict(self.__resolve_conversation_context(history), opts)

    def __resolve_conversation_context(self, context_input: LLMConversationContextInput) -> LLMContext:
        return {
            "history": [
                {"role": item.get("role", "user"), "content": [{"type": "text", "text": item.get("content", "")}]}
                for item in context_input
            ]
        }

    def predict(self, context: LLMContext, opts: LLMPredictionOpts | None = None) -> OngoingPrediction:
        """
        :alpha:
        """
        context = LLMContext.model_validate(context)
        opts = LLMPredictionOpts.model_validate(opts) if opts is not None else None

        # TODO splitOpts
        extra_opts = opts
        config = opts

        cancel_event, emit_cancel_event = BufferedEvent.create()
        ongoing_prediction, finished, failed, push = OngoingPrediction.create(emit_cancel_event)

        api_override_layer = {"layerName": "apiOverride", "config": prediction_config_to_kv_config(config)}
        prediction_layers = self.__internal_kv_config_stack.get("layers", [])
        prediction_layers.append(api_override_layer)

        self.__predict_internal(
            self.specifier,
            context,
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

    async def unstable_get_context_length(self) -> int:
        return (await self.get_load_config()).get("contextLength", -1)

    async def unstable_apply_prompt_template(
        self, context: LLMContext, opts: LLMApplyPromptTemplateOpts | None = None
    ) -> str:
        context = LLMContext.model_validate(context)
        opts = LLMApplyPromptTemplateOpts.model_validate(opts) if opts is not None else None
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

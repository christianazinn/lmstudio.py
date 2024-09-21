from abc import ABC
from typing import Dict, Optional, Union, Tuple

from ...dataclasses import (
    KVConfig,
    KVConfigStack,
    LLMCompletionContextInput,
    LLMContext,
    LLMConversationContextInput,
    LLMPredictionConfig,
    LLMPredictionExtraOpts,
    LLMPredictionOpts,
)


class BaseLLMDynamicHandle(ABC):
    _internal_kv_config_stack = KVConfigStack(layers=[])

    def number_to_checkbox_numeric(
        self, value: Optional[float], unchecked_value: float, value_when_unchecked: float
    ) -> Optional[Dict[str, Union[bool, float]]]:
        if value is None:
            return None
        if value == unchecked_value:
            return {"checked": False, "value": value_when_unchecked}
        if value != unchecked_value:
            return {"checked": True, "value": value}

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
                        "value": self.number_to_checkbox_numeric(prediction_config["max_predicted_tokens"], -1, 1),
                    }
                )
            if "repeat_penalty" in prediction_config:
                fields.append(
                    {
                        "key": "repeat_penalty",
                        "value": self.number_to_checkbox_numeric(prediction_config["repeat_penalty"], 1, 1),
                    }
                )
            if "min_p_sampling" in prediction_config:
                fields.append(
                    {
                        "key": "min_p_sampling",
                        "value": self.number_to_checkbox_numeric(prediction_config["min_p_sampling"], 0, 0.05),
                    }
                )
            if "top_p_sampling" in prediction_config:
                fields.append(
                    {
                        "key": "top_p_sampling",
                        "value": self.number_to_checkbox_numeric(prediction_config["top_p_sampling"], 1, 0.95),
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

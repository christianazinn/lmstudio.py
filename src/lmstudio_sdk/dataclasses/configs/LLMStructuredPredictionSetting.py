from typing import Any, Dict, Literal, Union


LLMStructuredPredictionSetting = Union[
    Dict[Literal["type"], Literal["none"]],
    Dict[Literal["type", "jsonSchema"], Union[Literal["json"], Any]],
]
# TODO: docstring
"""
Settings for structured prediction. Structured prediction is a way to force the model to generate
predictions that conform to a specific structure.

For example, you can use structured prediction to make the model only generate valid JSON, or
even JSON that conforms to a specific schema (i.e. having strict types).

Some examples:

Only generate valid JSON:

```python
prediction = model.complete("...", {
    "max_predicted_tokens": 100,
    "structured": {"type": "json"},
})
```

Only generate JSON that conforms to a specific schema (See https://json-schema.org/ for more
information on authoring JSON schema):

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
    },
    "required": ["name", "age"],
}
prediction = model.complete("...", {
    "max_predicted_tokens": 100,
    "structured": {"type": "json", "jsonSchema": schema},
})
```

By default, `{"type": "none"}` is used, which means no structured prediction is used.

Caveats:

- Although the model is forced to generate predictions that conform to the specified structure,
  the prediction may be interrupted (for example, if the user stops the prediction). When that
  happens, the partial result may not conform to the specified structure. Thus, always check the
  prediction result before using it, for example, by wrapping the `json.loads` inside a try-except
  block.
- In certain cases, the model may get stuck. For example, when forcing it to generate valid JSON,
  it may generate an opening brace `{` but never generate a closing brace `}`. In such cases, the
  prediction will go on forever until the context length is reached, which can take a long time.
  Therefore, it is recommended to always set a `max_predicted_tokens` limit.
"""

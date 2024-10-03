<p align="center">
  
  <picture> 
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/christianazinn/lmstudio-python/blob/assets/dark.png?raw=true">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/christianazinn/lmstudio-python/blob/assets/light.png?raw=true">
    <img alt="lmstudio python library logo" src="https://github.com/christianazinn/lmstudio-python/blob/assets/light.png?raw=true" width="290" height="86" style="max-width: 100%;">
  </picture>
  
</p>
<p align="center"><code>Use local LLMs in Python</code></p>
<p align="center"><i>Unofficial LM Studio Python Client SDK - Pre-Pre-Release</i></p>

### Pre-Pre-Release Pre-Alpha

This is an unofficial effort to port the functionality of the [`lmstudio.js` TypeScript SDK](https://github.com/lmstudio-ai/lmstudio.js) to Python.

Since the TypeScript SDK is in pre-release alpha, I guess this is in pre-pre-release pre-alpha while I work to get feature parity up.
Expect the library to be completely nonfunctional for the time being, and expect absurdly breaking changes!

Follow announcements about the base `lmstudio.js` library on [Twitter](https://lmstudio.ai/LMStudioAI) and [Discord](https://discord.gg/aPQfnNkxGC). Read the [TypeScript docs](https://lmstudio.ai/docs).

Discuss all things related to developing with LM Studio in <a href="https://discord.gg/aPQfnNkxGC">#dev-chat</a> in LM Studio's Community Discord server. Contact me at `@christianazinn` on Discord or via GitHub about this particular repository.
<a href="https://discord.gg/aPQfnNkxGC"><img alt="Discord" src="https://img.shields.io/discord/1110598183144399058?logo=discord&style=flat&logoColor=white"></a>

---

### Installation

```shell
pip install lmstudio_sdk
```

## Examples

### Loading an LLM and Predicting with It

```python
from lmstudio_sdk import LMStudioClient

client = LMStudioClient()
llama3 = client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")

for fragment in llama3.respond([{"role": "user", "content": "Say hello to lmstudio.py!"}], {}):
    print(fragment, end="", flush=True)

client.close()
```

Asynchronously, just `await` the constructor and use examples:

```python
import asyncio
from lmstudio_sdk import LMStudioClient

async def main():
    client = await LMStudioClient()
    llama3 = await client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")
    prediction = await llama3.respond([{"role": "user", "content": "Say hello to lmstudio.py!"}], {})

    async for fragment in prediction:
        print(fragment, end="", flush=True)

    await client.close()

asyncio.run(main())
```

> [!NOTE]
>
> If you wish to `await` on the result of the prediction rather than streaming it, note that the call to
> `model.respond()`/`model.complete()` will take **two** `await`s, like so:
>
> ```python
> result = await (await model.respond([{"role": "user", "content": "Say hello to lmstudio.py!"}]))
> ```

Henceforth all examples will be given synchronously; the asynchronous versions simply have `await` sprinkled in all over.

### Using a Non-Default LM Studio Server Port

This example shows how to connect to LM Studio running on a different port (e.g., 8080).

```python
from lmstudio_sdk import LMStudioClient

client = new LMStudioClient({"baseUrl": "ws://localhost:8080"})

# client.llm.load(...)
```

### Giving a Loaded Model a Friendly Name

You can set an identifier for a model when loading it. This identifier can be used to refer to the model later.

```python
client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF", {"identifier": "my-model",})

# You can refer to the model later using the identifier
my_model = client.llm.get("my-model")
# my_model.complete(...)
```

### Loading a Model with a Custom Configuration

By default, the load configuration for a model comes from the preset associated with the model (Can be changed on the "My Models" page in LM Studio).

```python
llama3 = client.llm.load(
    "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    {
        "config": {
            "context_length": 1024,
            "gpu_offload": 0.5,  # Offloads 50% of the computation to the GPU
        },
    }
)

# llama3.complete(...)
```

### Custom Loading Progress

You can track the loading progress of a model by providing an `on_progress` callback.

```python
llama3 = client.llm.load(
    "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
    {
        "verbose": False,  # Disables the default progress logging
        "on_progress": lambda progress: print(f"Progress: {round(progress * 100, 1)}")
    }
)
```

### Listing all Models that can be Loaded

If you wish to find all models that are available to be loaded, you can use the `list_downloaded_models` method on the `system` object.

```python
downloaded_models = client.system.list_downloaded_models()
downloaded_llms = [model for model in downloaded_models if model.type == "llm"]

# Load the first model
model = client.llm.load(downloaded_llms[0].path)
# model.complete(...);
```

### Canceling a Load

You can cancel a load by using an AbortSignal, ported from TypeScript.
This API will probably change with time. Currently we have one AbortSignal
class for each of sync and async.

```python
from lmstudio_sdk import SyncAbortSignal

signal = SyncAbortSignal()

try:
    llama3 = client.llm.load(
        "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        {"signal": signal,}
    )
  # llama3.complete(...);
except Exception as e:
    logger.error(e)

# Somewhere else in your code:
controller.abort()
```

### Unloading a Model

You can unload a model by calling the `unload` method.

```python
llama3 = client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF", {"identifier": "my-model"})

# ...Do stuff...

client.llm.unload("my-model")
```

Note, by default, all models loaded by a client are unloaded when the client disconnects. Therefore, unless you want to precisely control the lifetime of a model, you do not need to unload them manually.

### Using an Already Loaded Model

To look up an already loaded model by its identifier, use the following:

```python
my_model = client.llm.get({"identifier": "my-model"})
# Or just
my_model = client.llm.get("my-model")

# myModel.complete(...)
```

To look up an already loaded model by its path, use the following:

```python
# Matches any quantization
llama3 = client.llm.get({
    "path": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
})

# Or if a specific quantization is desired:
llama3 = client.llm.get({
    "path": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
})

# llama3.complete(...)
```

### Using any Loaded Model

If you do not have a specific model in mind, and just want to use any loaded model, you can use the `unstable_get_any` method:

```python
any_model = client.llm.unstable_get_any()
# any_model.complete(...)
```

### Listing All Loaded Models

To list all loaded models, use the `client.llm.list_loaded` method.

```python
loaded_models = client.llm.list_loaded()

if loadedModels.length == 0:
    raise Exception("No models loaded")

# Use the first one
const first_model = await client.llm.get({
    "identifier": loaded_models[0]["identifier"],
})
# first_model.complete(...);
```

> Example `list_loaded` Response:
>
> ```JSON
> [
>   {
>     "identifier": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
>     "path": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
>   },
>   {
>     "identifier": "microsoft/Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-q4.gguf",
>     "path": "microsoft/Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-q4.gguf",
>   },
> ]
> ```

### Text Completion

To perform text completion, use the `complete` method:

```python
prediction = model.complete("The meaning of life is")

for fragment in prediction:
    print(fragment, end="", flush=True)
```

Note that this would be an `async for` in asynchronous code.

By default, the inference parameters in the preset is used for the prediction. You can override them like this:

```python
const prediction = any_model.complete("Meaning of life is", {
    "contextOverflowPolicy": "stopAtLimit",
    "maxPredictedTokens": 100,
    "stopStrings": ["\n"],
    "temperature": 0.7,
})

# ...Do stuff with the prediction...
```

### Conversation

To perform a conversation, use the `respond` method:

```python
prediction = any_model.respond([
    { "role": "system", "content": "Answer the following questions." },
    { "role": "user", "content": "What is the meaning of life?" },
])

for fragment in prediction:
    print(fragment, end="", flush=True)
```

Similarly, you can override the inference parameters for the conversation (Note the available options are different from text completion):

```python
prediction = any_model.respond(
    [
        { "role": "system", "content": "Answer the following questions." },
        { "role": "user", "content": "What is the meaning of life?" },
    ],
    {
        "contextOverflowPolicy": "stopAtLimit",
        "maxPredictedTokens": 100,
        "stopStrings": ["\n"],
        "temperature": 0.7,
    }
)

# ...Do stuff with the prediction...
```

> [!IMPORTANT]
>
> _Always Provide the Full History/Context_
>
> LLMs are _stateless_. They do not remember or retain information from previous inputs. Therefore, when predicting with an LLM, you should always provide the full history/context.

### Getting Prediction Stats

If you wish to get the prediction statistics, you can await on the prediction object to get a `PredictionResult`, through which you can access the stats via the `stats` property.

```python
prediction = model.complete("The meaning of life is")

stats = prediction.result().stats
print(stats)
```

Asynchronously, this looks more like

```python
prediction = await model.complete("The meaning of life is")

stats = (await prediction).stats
print(stats)
```

> [!NOTE]
>
> **No Extra Waiting**
>
> When you have already consumed the prediction stream, awaiting on the prediction object will not cause any extra waiting, as the result is cached within the prediction object.
>
> On the other hand, if you only care about the final result, you don't need to iterate through the stream. Instead, you can await on the prediction object directly to get the final result. An example of what this looks like in JSON is below:
>
> ```JSON
> {
>   "stopReason": "eosFound",
>   "tokensPerSecond": 26.644333102146646,
>   "numGpuLayers": 33,
>   "timeToFirstTokenSec": 0.146,
>   "promptTokensCount": 5,
>   "predictedTokensCount": 694,
>   "totalTokensCount": 699
> }
> ```

### Producing JSON (Structured Output)

LM Studio supports structured prediction, which will force the model to produce content that conforms to a specific structure. To enable structured prediction, you should set the `structured` field. It is available for both `complete` and `respond` methods.

Here is an example of how to use structured prediction:

```python
prediction = model.complete("Here is a joke in JSON:", {
    "max_predicted_tokens": 100,
    "structured": {"type": "json"},
})

result = prediction.result()

try:
    # Although the LLM is guaranteed to only produce valid JSON, when it is interrupted, the
    # partial result might not be. Always check for errors. (See caveats below)
    parsed = json.loads(result.content)
    print(parsed)
except Exception as e:
    print(f"Error: {e}")
```

> Example output:
>
> ```JSON
> {
>  "title": "The Shawshank Redemption",
>  "genre": [ "drama", "thriller" ],
>  "release_year": 1994,
>  "cast": [
>    { "name": "Tim Robbins", "role": "Andy Dufresne" },
>    { "name": "Morgan Freeman", "role": "Ellis Boyd" }
>  ]
> }
> ```

Sometimes, any JSON is not enough. You might want to enforce a specific JSON schema. You can do this by providing a JSON schema to the `structured` field. Read more about JSON schema at [json-schema.org](https://json-schema.org/).

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

> [!IMPORTANT]
>
> **Caveats with Structured Prediction**
>
> - Although the model is forced to generate predictions that conform to the specified structure, the prediction may be interrupted (for example, if the user stops the prediction). When that happens, the partial result may not conform to the specified structure. Thus, always check the prediction result before using it, for example, by wrapping the `JSON.parse` inside a try-catch block.
> - In certain cases, the model may get stuck. For example, when forcing it to generate valid JSON, it may generate a opening brace `{` but never generate a closing brace `}`. In such cases, the prediction will go on forever until the context length is reached, which can take a long time. Therefore, it is recommended to always set a `maxPredictedTokens` limit. This also contributes to the point above.

### Canceling/Aborting a Prediction

A prediction may be canceled by calling the `cancel` method on the prediction object.

```python
prediction = model.complete("The meaning of life is")

# ...Do stuff...

prediction.cancel()
```

When a prediction is canceled, the prediction will stop normally but with `stopReason` set to `"userStopped"`. You can detect cancellation like so:

```python
for fragment in prediction:
    print(fragment, end="", flush=True)

stats = prediction.result().stats
if stats.stopReason == "userStopped":
    print("Prediciton was canceled by the user")
```

### Async vs. Sync

Asynchronous paradigms are typically best suited for LLM applications, considering how long inference can take. The `lmstudio.js` library, for instance, is written asynchronously, which is facilitated by JavaScript favoring asynchronous paradigms in general.

Python tends to favor synchronous programming; for instance, the OpenAI client runs synchronously. I designed this library so that it could in theory be used as a not-quite drop-in replacement, but very nearly one, for the OpenAI client (though of course only for LM Studio) - therefore synchronicity is a must. Many people also don't know how to use `asyncio` or don't care to for their purposes, so a synchronous client is provided for these users.

However, leveraging `asyncio` allows for greater control over program flow, so we also provide an asynchronous client for those who need it. Simply `await` the `LMStudioClient` constructor! The only quirk is that channel functions (`predict`, `complete`, `respond`, and `get`) will require you to await **twice**: once to send the request, and then once to get the result. For instance, if you just wanted the result, you could do the following:

```python
print(await(await model.respond(["role": "user", "content": "Hello world!"], {})))
```

but you could also use the output of the first `await` as an async iterable, like so:

```python
prediction = await model.respond(["role": "user", "content": "Hello world!"], {})
async for fragment in prediction:
    print(fragment, end="", flush=True)
```

Pick whichever backend best suits your use case. Incidentally, the asynchronous code runs on `websockets` while the synchronous code runs on `websocket-client` (confusingly imported as `websocket`).

### Logging

We provide internal logging for your debugging pleasure(?). Import the `lmstudio.py` logger using `from lmstudio_sdk import logger`, then `logger.setLevel` to one of the default `logging` levels, or one of the following (which can be imported from `lmstudio_sdk` as well):

- `RECV = 5`: debugs all packets sent _and received_ to/from the LM Studio server.
- `SEND = 7`: debugs all packets sent to the LM Studio server.
- `WEBSOCKET = 9`: debugs WebSocket connection events.

As usual, each level logs all levels above it. Depending on the backend, you can also use the `websocket-client` (sync) or `websockets` (async) loggers for more granular communications logging.

### Known Limitations

Currently aborting doesn't play very well with synchronous code. Preprocessors are not implemented, and please disregard TODOs.

Synchronous code is less tested than async code. Synchronous code might hang and not respect SIGINT if calling `result()` on a model load or prediction request. In fact this is a [known issue](https://bugs.python.org/issue35935) with the way `threading.Event.wait()` blocks.

Documentation is also still coming, as are unit tests - maybe there's a typo somewhere in untested code that causes a method to not function properly. This library isn't released yet for a reason.

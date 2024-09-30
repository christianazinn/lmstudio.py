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

### API Usage

```python
from lmstudio_sdk import LMStudioClient

client = LMStudioClient()
model = client.llm.unstable_get_any()

for fragment in model.respond([{"role": "user", "content": "Say hello to lmstudio.py!"}], {}):
    print(fragment, end="")

client.close()
```

Asynchronously:

```python
import asyncio
from lmstudio_sdk import LMStudioClient

async def main():
    client = await LMStudioClient()
    model = await client.llm.unstable_get_any()
    prediction = await model.respond([{"role": "user", "content": "Say hello to lmstudio.py!"}], {})

    async for fragment in prediction:
        print(fragment, end="")

    await client.close()

asyncio.run(main())
```

TODO: more examples

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
    print(fragment, end="")
```

Pick whichever backend best suits your use case. Incidentally, the asynchronous code runs on `websockets` while the synchronous code runs on `websocket-client` (confusingly imported as `websocket`).

### Logging

We provide internal logging for your debugging pleasure(?). Import the `lmstudio.py` logger using `from lmstudio_sdk import logger`, then `logger.setLevel` to one of the default `logging` levels, or one of the following (which can be imported from `lmstudio_sdk` as well):

- `RECV = 5`: debugs all packets sent _and received_ to/from the LM Studio server.
- `SEND = 7`: debugs all packets sent to the LM Studio server.
- `WEBSOCKET = 9`: debugs WebSocket connection events.

As usual, each level logs all levels above it. Depending on the backend, you can also use the `websocket-client` (sync) or `websockets` (async) loggers for more granular communications logging.

### Known Limitations

Currently aborting doesn't play very well with synchronous code. Synchronous code might hang and not respect SIGINT (Ctrl+C). Preprocessors are not implemented, nor are diagnostics (and all of the `DiagnosticsNamespace` at that). Please disregard TODOs.

Documentation is also still coming, as are unit tests - maybe there's a typo somewhere in untested code that causes a method to not function properly. This library isn't released yet for a reason.

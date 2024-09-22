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

print(model.respond([{"role": "user", "content": "Say hello to the LM Studio Python library!"}], {}))
```

TODO: whatever goes here
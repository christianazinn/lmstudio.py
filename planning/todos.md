TODO: figure out why auth takes forever
TODO: verbose and robust error handling
TODO: translate logger messages instead of using print statements
TODO: rewrite docstrings because they still have copy/pasted typescript annotations
TODO: unit tests!
TODO: de-asyncify logic: most people do not have a clue how to use asyncio, and python is worse at it than typescript, so make it easier for them. remove all use of asyncio
ideally do OpenAI style where you can enable streaming to use a typical "for x in y" iterator or disable streaming to block the main process until a response is received or times out
TODO: single vs double underscore naming
TODO: from **future** import annotations where necessary

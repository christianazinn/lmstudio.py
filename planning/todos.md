TODO: unit tests!
TODO: sync code does not respect SIGINT during blocking channel operations like load, respond (when using .result())
TODO: README + docs
TODO: preprocessors and generators, full feature parity

TODO TODO: some dataclasses are (or really should be) only ever generated internally, such as PredictionResult. these shoudl not be TypedDicts but rather objects so people can dot access them. figure out which ones these are! eg ModelDescriptor?

TODO TODO TODO: feature parity with all changes brought in by lmstudio.js PR #90 for chat history mostly, but also everything since PR #84 (commit d424b042012699c5d41f9dd3c5b3a5b33677f69d) with which this library is up to date apart from preprocessors

more design questions:
move from option typeddicts to function kwargs? more "Pythonic"?
pydantic runtime type checking? I guess the TS lib uses Zod

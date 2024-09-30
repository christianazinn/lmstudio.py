TODO: unit tests!
TODO: sync code does not respect SIGINT during blocking channel operations like load, respond (when using .result())
TODO: README + docs
TODO: preprocessors and generators, full feature parity

TODO: stylize according to Google style guide/PEP 8
https://google.github.io/styleguide/pyguide.htm
TODO: docstrings according to PEP 257
in particular module level imports, line length 79 (72 for multiline), no fstring logger calls

more design questions:
move from option typeddicts to function kwargs? more "Pythonic"?
pydantic runtime type checking? I guess the TS lib uses Zod

UTD since d424b042012699c5d41f9dd3c5b3a5b33677f69d otherwise

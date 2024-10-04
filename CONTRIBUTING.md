# Contributing to lmstudio.py

Hello! This temporary CONTRIBUTING.md file outlines the directory structure
and some quirks of the implementation that are not immediately obvious.
This file may be easier to read raw.

## General notes

To be noted first is that this project is as close a transliteration of the
TypeScript SDK into Python as I could manage. Some requirements may change
that in the future, and in fact I hope they will! This SDK need not be bound
by the TypeScript SDK; I hope rather that it will contain a superset of the
latter's features (insofar as that is achievable with the same API).

We should also do runtime type checking somehow. I couldn't figure out
where else to write this. We do a little bit on "primitives" but nothing
on most internal dataclasses.

If you take two things away from this document, please read the little
tidbit on sync/async under `/src/lmstudio_sdk/backend` and the note on
implementation under `/src/lmstudio_sdk/backend/communications/_client_port`.

## Directory structure

### /planning

My TODO list and a TypeScript file containing the
signatures of the remaining code to translate. Only preprocessors are left
(mostly) but there are some changes (mostly brought in lmstudio.js PR #90)
that this repo needs to be updated for. Otherwise we have parity up to
PR #84.

### /tests

Contains what very little of a unit test suite currently exists,
as well as a very small test script that can be changed at will.
Unit tests still need to be written; ideally I would like to have a test
suite that compares Python SDK behavior directly to the TypeScript SDK
for the most literal ensurance of feature parity.

### /src/lmstudio_sdk

Package source. All public API components and
some internal ones are documented. To rename the package to `lmstudio`,
a simple Ctrl+Shift+F find all and replace `lmstudio_sdk` with `lmstudio`
should do the trick.

#### /src/lmstudio_sdk/utils

Contains utilities and a few translated TypeScript
classes, notably AbortSignals and BufferedEvents. It also provides a logger
that logs a few more levels than default. This submodule should never
import from another submodule to avoid circular imports.

#### /src/lmstudio_sdk/dataclasses

Contains most interfaces and datatypes
translated from TypeScript as `typing.TypedDict`s. The exceptions are
the constructor opts, which are passed as kwargs into the constructor,
and certain types which are only ever constructed by the SDK (e.g.
`PredictionResult`) which are classes so the user can dot access them.
Currently we're in the midst of figuring out which such datatypes should
follow this pattern, and whether to retain the `TypedDict` argument pattern
or switch to a possibly more Pythonic kwarg pattern.

#### /src/lmstudio_sdk/backend

Where most of the actual logic occurs.
Currently we offer both asynchronous and synchronous clients, which
differ in their backend: the sync client uses the `websocket-client`
blocking design and the async client uses `websockets` and is tightly
integrated with `asyncio`. Efforts to reduce code duplication in light
of this cause a lot of problems and headaches and honestly poor choices
in the codebase which will be covered shortly.

I think I thought of "async/sync" and had the right _idea_ (see the short
manifesto at the end of README.md) but implemented it the wrong way:
WebSocket requests should take little enough time that it doesn't matter
whether we run them synchronously or asynchronously, and switching
to a single backend implementation would considerably simplify the codebase.

Instead, we should return `asyncio.Future`s and similar (see the async
implementation of a streamable iterator) to asynchronous code so RPC calls
(which have considerably greater latency than sending the request itself,
in no small part due to the obvious fact that the request is part of the call)
or model loading/inference can be awaited, not just the literal packet sending.
I will try to work on this in the near future pending assurance that it
is a decent idea.

In any case, here are the submodules of `/src/lmstudio_sdk/backend`:

##### /src/lmstudio_sdk/client

Client objects for the user to interact with. Includes a factory
method `LMStudioClient` (confusingly not in the `LMStudioClient.py` file:
this should be renamed to `BaseLMStudioClient`) that dynamically connects,
authenticates, and returns an async or sync client depending on
whether it is `await`ed; it uses a bit of a hack to determine this.
The client behaves the same way as in the TypeScript SDK
with namespaces dot accessible.

##### /src/lmstudio_sdk/communications

`/communications` has two submodules itself and is the "transport" backend.

###### /src/lmstudio_sdk/communications/\_client_port

Contains the proper backend logic. Although the module
is private, each class is thoroughly documented - see the source code.
There is a `BaseClientPort` that provides the internal API
for server communication to be used by the rest of the code, and this
is subclassed by async and sync versions that implement the respective
backends.

The most non-obvious part of the implementation is here in `/_client_port`:
to allow the same top-level public API code to run sync and async (e.g.
`client.llm.load()`), each function in the call stack returns the result
of the function below it, which eventually reaches the backend; this is then
either an awaitable `Coroutine` for the async backend or a typical process
for the sync backend, allowing the same method to technically be both
`await`ed and invoked normally. The problem is then that we are not given
the chance to do any postprocessing past the point at which we need
to invoke the backend, i.e. send a payload over the WebSocket. The way
we get around this is by passing a callback and an `extra` dict all the way
down the call stack, which is then handled in the backend function after
the payload is sent to do "postprocessing". This feels like a terrible idea,
but it works for now - if the sync/async distinction is redone as outlined
above, this should really go.

###### /src/lmstudio_sdk/communications/ongoing_prediction

Contains objects representing ongoing predictions.
The sync version acts as a streamable iterator (so you can wait for the
full result by calling `.result()` or iterate over chunks as they are
generated with `for fragment in ongoing_prediction`), and the async
version acts as an async streamable iterator (so you can `await`
directly on the object or iterate with `async for...`). The difference
between `await`ing directly on the object and calling `result()` doesn't
feel quite right, which should probably be fixed. These also use internal
`utils.BufferedEvent`s (transliterated from TypeScript) to handle cancel
callbacks.

##### /src/lmstudio_sdk/handles

Contains the code for interacting with models based on a specifier
or instance reference. These are broadly documented since most of it
is part of the public API. `LLMDynamicHandle` in particular is
fairly complicated and poorly commented (sorry!) but hopefully the logic
is readable and whatever isn't is probably identical to whatever it is
in the TypeScript SDK in function.

##### /src/lmstudio_sdk/namespaces

Contains the dot-accessed namespaces on the client object.
Each of these essentially wraps a client port (from `/_client_port`) and
provides the API for interacting with it, hence we have two or three
"wrapper" layers: the backend WebSocket is wrapped in a `ClientPort`, then
this is wrapped in a `Namespace` and these namespaces are encapsulated in
a `LMStudioClient`. System and diagnostics namespaces have very little code
just because there's pretty much nothing to be done, while both embedding
and LLM namespaces are `ModelNamespace`s: much like `LLMDynamicHandle`,
things have docstrings but implementation is poorly commented, though
the logic should be readable and function is comparable to the TS SDK.

---

Last updated October 3, 2024;
Christian Zhou-Zheng, Element Labs

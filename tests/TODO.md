for each of sync, async:

- test client constructors
- test methods:
  - system:
    - list_downloaded_models
  - llm and embedding:
    - load
    - unload
    - list_loaded
    - get
    - unstable_get_any
    - unstable_get_or_load
  - embedding handles:
    - get_model_info
    - get_load_config
    - embed_string
    - unstable_get_context_length
    - unstable_get_eval_batch_size
    - unstable_tokenize
  - llm handles:
    - get_model_info
    - get_load_config
    - complete
    - respond
    - predict
    - unstable_get_context_length
    - unstable_apply_prompt_template
    - unstable_tokenize
    - unstable_count_tokens
  - aborting model load and any prediction process
  - getting response directly and iterating over chunks

::how much of these can actually be unit tests and how much
will require qualitative review?
-> git LFS or submodule, ~~package a small embedding model~~ use packaged nomic and package an LLM and then test by pointing LM Studio to the packaged models folder
::should we compare against a benchmark test suite in ts?
-> yes: try static and dynamic test kits
also ensure you set generation to deterministic

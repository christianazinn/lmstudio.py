// TODO: REMEMBER TO ADD CONSTRUCTORS FOR EVERYTHING!!!!!
// TODO: also standardize fields to underscores

/**
 * Abstract namespace for namespaces that deal with models.
 *
 * @public
 */
export declare abstract class ModelNamespace<TLoadModelConfig, TDynamicHandle extends DynamicHandle, TSpecificModel> {
  /**
   * Load a model for inferencing. The first parameter is the model path. The second parameter is an
   * optional object with additional options. By default, the model is loaded with the default
   * preset (as selected in LM Studio) and the verbose option is set to true.
   *
   * When specifying the model path, you can use the following format:
   *
   * `<publisher>/<repo>[/model_file]`
   *
   * If `model_file` is not specified, the first (sorted alphabetically) model in the repository is
   * loaded.
   *
   * To find out what models are available, you can use the `lms ls` command, or programmatically
   * use the `client.system.listDownloadedModels` method.
   *
   * Here are some examples:
   *
   * Loading Llama 3:
   *
   * ```typescript
   * const model = await client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF");
   * ```
   *
   * Loading a specific quantization (q4_k_m) of Llama 3:
   *
   * ```typescript
   * const model = await client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf");
   * ```
   *
   * To unload the model, you can use the `client.llm.unload` method. Additionally, when the last
   * client with the same `clientIdentifier` disconnects, all models loaded by that client will be
   * automatically unloaded.
   *
   * Once loaded, see {@link LLMDynamicHandle} or {@link EmbeddingDynamicHandle} for how to use the
   * model for inferencing or other things you can do with the model.
   *
   * @param path - The path of the model to load.
   * @param opts - Options for loading the model.
   * @returns A promise that resolves to the model that can be used for inferencing
   */
  load(path: string, opts?: BaseLoadModelOpts<TLoadModelConfig>): Promise<TSpecificModel>;
  /**
   * Unload a model. Once a model is unloaded, it can no longer be used. If you wish to use the
   * model afterwards, you will need to load it with {@link LLMNamespace#loadModel} again.
   *
   * @param identifier - The identifier of the model to unload.
   */
  unload(identifier: string): Promise<void>;
  /**
   * List all the currently loaded models.
   */
  listLoaded(): Promise<Array<ModelDescriptor>>;
  /**
   * Get a specific model that satisfies the given query. The returned model is tied to the specific
   * model at the time of the call.
   *
   * For more information on the query, see {@link ModelQuery}.
   *
   * @example
   *
   * If you have loaded a model with the identifier "my-model", you can use it like this:
   *
   * ```ts
   * const model = await client.llm.get({ identifier: "my-model" });
   * const prediction = model.complete("...");
   * ```
   *
   * Or just
   *
   * ```ts
   * const model = await client.llm.get("my-model");
   * const prediction = model.complete("...");
   * ```
   *
   * @example
   *
   * Use the Gemma 2B IT model (given it is already loaded elsewhere):
   *
   * ```ts
   * const model = await client.llm.get({ path: "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF" });
   * const prediction = model.complete("...");
   * ```
   */
  get(query: ModelQuery): Promise<TSpecificModel>;
  /**
   * Get a specific model by its identifier. The returned model is tied to the specific model at the
   * time of the call.
   *
   * @example
   *
   * If you have loaded a model with the identifier "my-model", you can use it like this:
   *
   * ```ts
   * const model = await client.llm.get("my-model");
   * const prediction = model.complete("...");
   * ```
   *
   */
  get(path: string): Promise<TSpecificModel>;
  unstable_getAny(): Promise<TSpecificModel>;
  /**
   * Get a dynamic model handle for any loaded model that satisfies the given query.
   *
   * For more information on the query, see {@link ModelQuery}.
   *
   * Note: The returned `LLMModel` is not tied to any specific loaded model. Instead, it represents
   * a "handle for a model that satisfies the given query". If the model that satisfies the query is
   * unloaded, the `LLMModel` will still be valid, but any method calls on it will fail. And later,
   * if a new model is loaded that satisfies the query, the `LLMModel` will be usable again.
   *
   * You can use {@link LLMDynamicHandle#getModelInfo} to get information about the model that is
   * currently associated with this handle.
   *
   * @example
   *
   * If you have loaded a model with the identifier "my-model", you can use it like this:
   *
   * ```ts
   * const dh = client.llm.createDynamicHandle({ identifier: "my-model" });
   * const prediction = dh.complete("...");
   * ```
   *
   * @example
   *
   * Use the Gemma 2B IT model (given it is already loaded elsewhere):
   *
   * ```ts
   * const dh = client.llm.createDynamicHandle({ path: "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF" });
   * const prediction = dh.complete("...");
   * ```
   *
   * @param query - The query to use to get the model.
   */
  createDynamicHandle(query: ModelQuery): TDynamicHandle;
  /**
   * Get a dynamic model handle by its identifier.
   *
   * Note: The returned `LLMModel` is not tied to any specific loaded model. Instead, it represents
   * a "handle for a model with the given identifier". If the model with the given identifier is
   * unloaded, the `LLMModel` will still be valid, but any method calls on it will fail. And later,
   * if a new model is loaded with the same identifier, the `LLMModel` will be usable again.
   *
   * You can use {@link LLMDynamicHandle#getModelInfo} to get information about the model that is
   * currently associated with this handle.
   *
   * @example
   *
   * If you have loaded a model with the identifier "my-model", you can get use it like this:
   *
   * ```ts
   * const dh = client.llm.createDynamicHandle("my-model");
   * const prediction = dh.complete("...");
   * ```
   *
   * @param identifier - The identifier of the model to get.
   */
  createDynamicHandle(identifier: string): TDynamicHandle;
  /**
   * Extremely early alpha. Will cause errors in console. Can potentially throw if called in
   * parallel. Do not use in production yet.
   */
  unstable_getOrLoad(identifier: string, path: string, loadOpts?: BaseLoadModelOpts<TLoadModelConfig>): Promise<TSpecificModel>;
}
/**
 * This represents a set of requirements for a model. It is not tied to a specific model, but rather
 * to a set of requirements that a model must satisfy.
 *
 * For example, if you got the model via `client.llm.get("my-identifier")`, you will get a
 * `LLMModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
 * another model is loaded with the same identifier, using the same `LLMModel` will use the new
 * model.
 *
 * @public
 */
export declare abstract class DynamicHandle {
    /**
     * Gets the information of the model that is currently associated with this `LLMModel`. If no
     * model is currently associated, this will return `undefined`.
     *
     * Note: As models are loaded/unloaded, the model associated with this `LLMModel` may change at
     * any moment.
     */
    getModelInfo(): Promise<ModelDescriptor | undefined>;
    protected getLoadConfig(stack: string): Promise<KVConfig>;
}

/**
 * This represents a set of requirements for a model. It is not tied to a specific model, but rather
 * to a set of requirements that a model must satisfy.
 *
 * For example, if you got the model via `client.embedding.get("my-identifier")`, you will get a
 * `EmbeddingModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
 * another model is loaded with the same identifier, using the same `EmbeddingModel` will use the
 * new model.
 *
 * @public
 */
export declare class EmbeddingDynamicHandle extends DynamicHandle {
    embedString(inputString: string): Promise<{
        embedding: number[];
    }>;
    unstable_getContextLength(): Promise<number>;
    unstable_getEvalBatchSize(): Promise<number>;
    unstable_tokenize(inputString: string): Promise<number[]>;
}

/** @public */
export declare class EmbeddingNamespace extends ModelNamespace<EmbeddingLoadModelConfig, EmbeddingDynamicHandle, EmbeddingSpecificModel> {
}

/**
 * Represents a specific loaded Embedding. Most Embedding related operations are inherited from
 * {@link EmbeddingDynamicHandle}.
 *
 * @public
 */
export declare class EmbeddingSpecificModel extends EmbeddingDynamicHandle implements SpecificModel {
    readonly identifier: string;
    readonly path: string;
}

/**
 * This represents a set of requirements for a model. It is not tied to a specific model, but rather
 * to a set of requirements that a model must satisfy.
 *
 * For example, if you got the model via `client.llm.get("my-identifier")`, you will get a
 * `LLMModel` for the model with the identifier `my-identifier`. If the model is unloaded, and
 * another model is loaded with the same identifier, using the same `LLMModel` will use the new
 * model.
 *
 * @public
 */
export declare class LLMDynamicHandle extends DynamicHandle {
    /**
     * Use the loaded model to predict text.
     *
     * This method returns an {@link OngoingPrediction} object. An ongoing prediction can be used as a
     * promise (if you only care about the final result) or as an async iterable (if you want to
     * stream the results as they are being generated).
     *
     * Example usage as a promise (Resolves to a {@link PredictionResult}):
     *
     * ```typescript
     * const result = await model.complete("When will The Winds of Winter be released?");
     * console.log(result.content);
     * ```
     *
     * Or
     *
     * ```typescript
     * model.complete("When will The Winds of Winter be released?")
     *  .then(result =\> console.log(result.content))
     *  .catch(error =\> console.error(error));
     * ```
     *
     * Example usage as an async iterable (streaming):
     *
     * ```typescript
     * for await (const fragment of model.complete("When will The Winds of Winter be released?")) {
     *   process.stdout.write(fragment);
     * }
     * ```
     *
     * If you wish to stream the result, but also getting the final prediction results (for example,
     * you wish to get the prediction stats), you can use the following pattern:
     *
     * ```typescript
     * const prediction = model.complete("When will The Winds of Winter be released?");
     * for await (const fragment of prediction) {
     *   process.stdout.write(fragment);
     * }
     * const result = await prediction;
     * console.log(result.stats);
     * ```
     *
     * @param prompt - The prompt to use for prediction.
     * @param opts - Options for the prediction.
     */
    complete(prompt: LLMCompletionContextInput, opts?: LLMPredictionOpts): OngoingPrediction;
    private resolveCompletionContext;
    /**
     * Use the loaded model to generate a response based on the given history.
     *
     * This method returns an {@link OngoingPrediction} object. An ongoing prediction can be used as a
     * promise (if you only care about the final result) or as an async iterable (if you want to
     * stream the results as they are being generated).
     *
     * Example usage as a promise (Resolves to a {@link PredictionResult}):
     *
     * ```typescript
     * const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
     * const result = await model.respond(history);
     * console.log(result.content);
     * ```
     *
     * Or
     *
     * ```typescript
     * const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
     * model.respond(history)
     *  .then(result => console.log(result.content))
     *  .catch(error => console.error(error));
     * ```
     *
     * Example usage as an async iterable (streaming):
     *
     * ```typescript
     * const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
     * for await (const fragment of model.respond(history)) {
     *   process.stdout.write(fragment);
     * }
     * ```
     *
     * If you wish to stream the result, but also getting the final prediction results (for example,
     * you wish to get the prediction stats), you can use the following pattern:
     *
     * ```typescript
     * const history = [{ role: 'user', content: "When will The Winds of Winter be released?" }];
     * const prediction = model.respond(history);
     * for await (const fragment of prediction) {
     *   process.stdout.write(fragment);
     * }
     * const result = await prediction;
     * console.log(result.stats);
     * ```
     *
     * @param history - The LLMChatHistory array to use for generating a response.
     * @param opts - Options for the prediction.
     */
    respond(history: LLMConversationContextInput, opts?: LLMPredictionOpts): OngoingPrediction;
    private resolveConversationContext;
    /**
     * @alpha
     */
    predict(context: LLMContext, opts: LLMPredictionOpts): OngoingPrediction;
    unstable_getContextLength(): Promise<number>;
    unstable_applyPromptTemplate(context: LLMContext, opts?: LLMApplyPromptTemplateOpts): Promise<string>;
    unstable_tokenize(inputString: string): Promise<number[]>;
}

/** @public */
export declare class LLMNamespace extends ModelNamespace<LLMLoadModelConfig, LLMDynamicHandle, LLMSpecificModel> {
}


/**
 * Represents a specific loaded LLM. Most LLM related operations are inherited from
 * {@link LLMDynamicHandle}.
 *
 * @public
 */
export declare class LLMSpecificModel extends LLMDynamicHandle implements SpecificModel {
    readonly identifier: string;
    readonly path: string;
}



/** @public */
export declare class LMStudioClient {
    readonly clientIdentifier: string;
    readonly llm: LLMNamespace;
    readonly embedding: EmbeddingNamespace;
    readonly system: SystemNamespace;
    readonly diagnostics: DiagnosticsNamespace;
    private isLocalhostWithGivenPortLMStudioServer;
    /**
     * Guess the base URL of the LM Studio server by visiting localhost on various default ports.
     */
    private guessBaseUrl;
    constructor(opts?: LMStudioClientConstructorOpts);
}

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

/**
 * Controller for a citation block in the prediction process. Currently cannot do anything.
 *
 * @public
 */
export declare class PredictionProcessCitationBlockController implements PredictionStepController {
    private readonly controller;
    private readonly id;
    constructor(controller: PromptPreprocessController, id: string);
}

/**
 * Controller for a debug info block in the prediction process. Currently cannot do anything.
 *
 * @public
 */
export declare class PredictionProcessDebugInfoBlockController implements PredictionStepController {
    private readonly controller;
    private readonly id;
    constructor(controller: PromptPreprocessController, id: string);
}

/**
 * Controller for a status block in the prediction process.
 *
 * @public
 */
export declare class PredictionProcessStatusController implements PredictionStepController {
    private readonly controller;
    private readonly id;
    private readonly indentation;
    constructor(controller: PromptPreprocessController, initialState: StatusStepState, id: string, indentation?: number);
    private lastSubStatus;
    private lastState;
    setText(text: string): void;
    setState(state: StatusStepState): void;
    private getNestedLastSubStatusBlockId;
    addSubStatus(initialState: StatusStepState): PredictionProcessStatusController;
}

/**
 * Controller for a prompt preprocessing session. Controller can be used to show status, debug info,
 * and/or citation blocks to the user in LM Studio.
 *
 * @public
 */
export declare class PromptPreprocessController {
    readonly abortSignal: AbortSignal;
    private endedFlag;
    private stepControllers;
    /**
     * Get the previous context. Does not include the current user message.
     */
    getContext(): ProcessorInputContext;
    /**
     * Get the current user message. i.e. the message that this preprocessor needs to process.
     */
    getUserMessage(): ProcessorInputMessage;
    createStatus(initialState: StatusStepState): PredictionProcessStatusController;
    createCitationBlock(citedText: string, source: CitationSource): PredictionProcessCitationBlockController;
    debug(...messages: Array<any>): void;
    /**
     * Throws an error if the prediction process has been aborted. Sprinkle this throughout your code
     * to ensure that the prediction process is aborted as soon as possible.
     */
    abortGuard(): void;
}

/**
 * @public
 */
export declare interface SpecificModel extends DynamicHandle {
    readonly identifier: string;
    readonly path: string;
}


/** @public */
export declare class SystemNamespace {
    private readonly systemPort;
    /**
     * List all downloaded models.
     * @public
     */
    listDownloadedModels(): Promise<Array<DownloadedModel>>;
}

export { }

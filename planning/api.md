# LMStudioClient

## Constructor args

- logger?: info, error, warn, debug (...messages: Array<unknown>) -> void
- baseUrl?: string
- verboseErrorMessages?: boolean
- clientIdentifier?: string
- clientPasskey?: string

## Fields

- clientIdentifier: string
- clientPasskey: string
- llm: LLMNamespace
- embedding: EmbeddingNamespace
- system: SystemNamespace
- diagnostics: DiagnosticsNamespace
- retrieval: RetrievalNamespace (todo)

# ModelNamespace

Generic<
TClientPort extends BaseModelPort,
TLoadModelConfig,
TDynamicHandle extends DynamicHandle<TClientPort>,
TSpecificModel

>

## Methods

- async load(path: string, opts: BaseLoadModelOpts<TLoadModelConfig>) -> Promise<TSpecificModel>
- unload(identifier: string): void
- listLoaded(): Promise<Array<ModelDescriptor>>
- get(query: ModelQuery): Promise<TSpecificModel>
- get(path: string): Promise<TSpecificModel>
- async unstable_getAny(): Promise<TSpecificModel>
- createDynamicHandle(query: ModelQuery): TDynamicHandle
- createDynamicHandle(identifier: string): TDynamicHandle
- createDynamicHandleFromInstanceReference(instanceReference: string): TDynamicHandle
- async unstable_getOrLoad(
  identifier: string,
  path: string,
  loadOpts?: BaseLoadModelOpts<TLoadModelConfig>
  ): Promise<TSpecificModel>

### BaseLoadModelOpts<TLoadModelConfig>

- identifier?: string
- config? TLoadModelConfig
- signal?: AbortSignal
- verbose: boolean | "debug" | "info" | "warn" | "error"
- onProgress?: (progress: number) => void

# LLMNamespace

extends ModelNamespace, all T are LLM

## Methods

- registerPromptPreprocessor(promptPreprocessor: PromptPreprocessor)

# EmbeddingNamespace

extends ModelNamespace

# SystemNamespace

## Methods

- async listDownloadedModels(): Promise<Array<DownloadedModel>>

# DiagnosticsNamespace

## Methods

- unstable_streamLogs(listener: (logEvent: DiagnosticsLogEvent) => void): () => void

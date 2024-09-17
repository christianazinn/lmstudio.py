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

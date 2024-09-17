


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
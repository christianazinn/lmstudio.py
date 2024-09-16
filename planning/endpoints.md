# API Endpoints Summary

## RPC Endpoints

### 1. echo
- **Type**: RPC
- **Parameters**:
  - `parameter`: string
- **Returns**: string

### 2. unloadModel
- **Type**: RPC
- **Parameters**:
  - `identifier`: string
- **Returns**: void

### 3. listLoaded
- **Type**: RPC
- **Parameters**: none
- **Returns**: array of llmDescriptorSchema

### 4. getModelInfo
- **Type**: RPC
- **Parameters**:
  - `specifier`: llmModelSpecifierSchema
  - `throwIfNotFound`: boolean
- **Returns**: optional object
  - `sessionIdentifier`: string
  - `descriptor`: llmDescriptorSchema

### 5. listDownloadedModels
- **Type**: RPC
- **Parameters**: none
- **Returns**: filteredArray(downloadedModelSchema)

### 6. getLoadConfig
- **Type**: RPC
- **Parameters**: 
  - `specifier`: One of two objects:
    1. Query type:
       - `type`: "query"
       - `query`: object
         - `domain`: optional ("embedding" | "llm" | undefined)
         - `identifier`: optional (string | undefined)
         - `path`: optional (string | undefined)
    2. Instance Reference type:
       - `type`: "instanceReference"
       - `instanceReference`: string
- **Returns**: object
  - `fields`: array of objects
    - `key`: string
    - `value`: any (optional)

### 7. embedString
- **Type**: RPC
- **Parameters**:
  - `modelSpecifier`: One of two objects:
    1. Query type:
       - `type`: "query"
       - `query`: object
         - `domain`: optional ("embedding" | "llm" | undefined)
         - `identifier`: optional (string | undefined)
         - `path`: optional (string | undefined)
    2. Instance Reference type:
       - `type`: "instanceReference"
       - `instanceReference`: string
  - `inputString`: string
- **Returns**: object
  - `embedding`: array of numbers

### 8. tokenize
- **Type**: RPC
- **Parameters**:
  - `specifier`: One of two objects:
    1. Query type:
       - `type`: "query"
       - `query`: object
         - `domain`: optional ("embedding" | "llm" | undefined)
         - `identifier`: optional (string | undefined)
         - `path`: optional (string | undefined)
    2. Instance Reference type:
       - `type`: "instanceReference"
       - `instanceReference`: string
  - `inputString`: string
- **Returns**: object
  - `tokens`: array of numbers

### 9. applyPromptTemplate
- **Type**: RPC
- **Parameters**:
  - `specifier`: One of two objects:
    1. Query type:
       - `type`: "query"
       - `query`: object
         - `domain`: optional ("embedding" | "llm" | undefined)
         - `identifier`: optional (string | undefined)
         - `path`: optional (string | undefined)
    2. Instance Reference type:
       - `type`: "instanceReference"
       - `instanceReference`: string
  - `context`: object
    - `history`: array of objects
      - `role`: string
      - `content`: array of objects (one of two types)
        1. Text type:
           - `type`: "text"
           - `text`: string
        2. Image type:
           - `type`: "imageBase64"
           - `base64`: string
  - `predictionConfigStack`: object
    - `layers`: array of objects
      - `layerName`: "currentlyLoaded" | "apiOverride" | "conversationSpecific" | "conversationGlobal" | "httpServerRequestOverride" | "completeModeFormatting" | "instance" | "userModelDefault" | "virtualModel" | "modelDefault"
      - `config`: object
        - `fields`: array of objects
          - `key`: string
          - `value`: any (optional)
  - `opts`: object
    - `omitBosToken`: boolean (optional)
    - `omitEosToken`: boolean (optional)
- **Returns**: object
  - `formatted`: string

## Channel Endpoints

### 1. loadModel
- **Type**: Channel
- **Creation Parameters**:
  - `path`: string
  - `identifier`: optional string
  - `preset`: optional string
  - `config`: llmLoadModelConfigSchema
  - `noHup`: boolean
- **To Client Packets**:
  - Progress type:
    - `type`: "progress"
    - `progress`: number
  - Success type:
    - `type`: "success"
    - `sessionIdentifier`: string
- **To Server Packets**:
  - Cancel type:
    - `type`: "cancel"

### 2. predict
- **Type**: Channel
- **Creation Parameters**:
  - `modelSpecifier`: llmModelSpecifierSchema
  - `history`: llmChatHistorySchema
  - `config`: llmFullPredictionConfigSchema
  - `structured`: optional llmStructuredPredictionSettingSchema
- **To Client Packets**:
  - Fragment type:
    - `type`: "fragment"
    - `fragment`: string
  - Success type:
    - `type`: "success"
    - `stats`: llmPredictionStatsSchema
    - `modelInfo`: llmDescriptorSchema
- **To Server Packets**:
  - Cancel type:
    - `type`: "cancel"

### 3. streamLogs
- **Type**: Channel
- **Creation Parameters**: none
- **To Client Packets**:
  - Log type:
    - `type`: "log"
    - `log`: diagnosticsLogEventSchema
- **To Server Packets**:
  - Stop type:
    - `type`: "stop"

### 4. registerPromptPreprocessor
- **Type**: Channel
- **Creation Parameters**:
  - `identifier`: string

- **To Server Packets**: One of the following types:
  1. Update type:
     - `type`: "update"
     - `taskId`: string
     - `update`: One of the following types:
       - PromptPreprocessorUpdateStatusCreate
       - PromptPreprocessorUpdateStatusUpdate
       - PromptPreprocessorUpdateStatusRemove
       - PromptPreprocessorUpdateCitationBlockCreate
       - PromptPreprocessorUpdateDebugInfoBlockCreate
  2. Complete type:
     - `type`: "complete"
     - `taskId`: string
     - `processed`: object
       - `text`: string
       - `role`: "system" | "user" | "assistant"
       - `files`: array of objects
         - `type`: "unknown" | "image" | "text/plain" | "text/other" | "application/pdf" | "application/word"
         - `sizeBytes`: number
         - `identifier`: string
  3. Error type:
     - `type`: "error"
     - `taskId`: string
     - `error`: object
       - `title`: string
       - `cause`: string (optional)
       - `suggestion`: string (optional)
       - `errorData`: Record<string, unknown> (optional)
       - `displayData`: One of the following types (optional):
         - Generic Specific Model Unloaded:
           - `code`: "generic.specificModelUnloaded"
         - Generic No Model Matching Query:
           - `code`: "generic.noModelMatchingQuery"
           - `query`: object (domain, identifier, path - all optional)
           - `loadedModelsSample`: array of strings
           - `totalLoadedModels`: number
         - LLM Path Not Found:
           - `code`: "llm.pathNotFound"
           - `path`: string
           - `availablePathsSample`: array of strings
           - `totalModels`: number
         - LLM Identifier Not Found:
           - `code`: "llm.identifierNotFound"
           - `identifier`: string
           - `loadedModelsSample`: array of strings
           - `totalLoadedModels`: number
       - `stack`: string (optional)
       - `rootTitle`: string (optional)

- **To Client Packets**: One of the following types:
  1. Preprocess type:
     - `type`: "preprocess"
     - `context`: object
       - `history`: array of objects
         - `text`: string
         - `role`: "system" | "user" | "assistant"
         - `files`: array of objects
           - `type`: "unknown" | "image" | "text/plain" | "text/other" | "application/pdf" | "application/word"
           - `sizeBytes`: number
           - `identifier`: string
     - `taskId`: string
     - `userInput`: object
       - `text`: string
       - `role`: "system" | "user" | "assistant"
       - `files`: array of objects (same structure as in history)
  2. Cancel type:
     - `type`: "cancel"
     - `taskId`: string
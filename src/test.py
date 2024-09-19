import asyncio

from lmstudio_sdk.LMStudioClient import LMStudioClient


async def main():
    # TODO: your errors are indented
    llm_client = await LMStudioClient.create({"base_url": "ws://localhost:1234"})
    try:
        # model_path = "lmstudio-community/gemma-2-2b-it-GGUF/gemma-2-2b-it-Q8_0.gguf"
        # model_path = "Qwen/Qwen2-0.5B-Instruct-GGUF/qwen2-0_5b-instruct-q4_0.gguf"
        # model_path = "qwen2"

        # result = await llm_client.getLoadConfig(model_path)
        print(await llm_client.system.list_downloaded_models())
        model = llm_client.llm.unstable_get_any()
        # TODO unasyncify this
        result = await model.respond([{"role": "user", "content": "Hello, how are you?"}], {})
        # async for completion in result:
        #     print(completion)
        # TODO result does not properly close
        print(type(result))
        # result = await llm_client.load_model(model_path)
        print("Model loaded:", result)

        # async for completion in llm_client.predict(model_path):
        #    print(completion)
    finally:
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())

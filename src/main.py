import asyncio

from LMStudioClient import LMStudioClient


async def main():
    llm_client = LMStudioClient("ws://localhost:1234/llm")
    try:
        await llm_client.connect()

        # model_path = "lmstudio-community/gemma-2-2b-it-GGUF/gemma-2-2b-it-Q8_0.gguf"
        model_path = "Qwen/Qwen2-0.5B-Instruct-GGUF/qwen2-0_5b-instruct-q4_0.gguf"
        model_path = "qwen2"

        result = await llm_client.getLoadConfig(model_path)
        # result = await llm_client.load_model(model_path)
        print("Model loaded:", result)

        # async for completion in llm_client.predict(model_path):
        #    print(completion)
    finally:
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())

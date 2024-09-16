import asyncio
from LMStudioClient import LMStudioClient


async def main():
    llm_client = LMStudioClient("ws://localhost:1234/llm")
    try:
        await llm_client.connect()

        result = await llm_client.unload_model(
            "lmstudio-community/gemma-2-2b-it-GGUF/gemma-2-2b-it-Q8_0.gguf"
        )
        print("Model loaded:", result)
    finally:
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())

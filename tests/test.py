from lmstudio_sdk import LMStudioClient, logger
import asyncio

logger.setLevel(10)


async def main():
    llm_client = await LMStudioClient(base_url="ws://localhost:1234")
    try:
        print(await llm_client.system.list_downloaded_models())

        model = await llm_client.llm.get("qwen2")

        result = await model.respond([{"role": "user", "content": "Tell me a long story."}], {})
        # print(await result)
        async for completion in result:
            print(completion)

        tokenCount = await model.unstable_tokenize("Hello, how are you?")
        print("Token count:", tokenCount)

        contextLength = await model.unstable_get_context_length()
        print("Context length:", contextLength)
    finally:
        await llm_client.close()


def syncmain():
    client = LMStudioClient()
    model = client.llm.unstable_get_any()

    prediction = model.respond([{"role": "user", "content": "Tell me a long story."}], {})

    for fragment in prediction:
        print(fragment, end="")


if __name__ == "__main__":
    # syncmain()
    asyncio.run(main())

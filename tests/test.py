from lmstudio_sdk import LMStudioClient, logger
import asyncio

logger.setLevel(10)


async def main():
    llm_client = await LMStudioClient(base_url="ws://localhost:1234")
    try:
        # model_path = "lmstudio-community/gemma-2-2b-it-GGUF/gemma-2-2b-it-Q8_0.gguf"
        # model_path = "Qwen/Qwen2-0.5B-Instruct-GGUF/qwen2-0_5b-instruct-q4_0.gguf"
        # model_path = "qwen2"

        print(await llm_client.system.list_downloaded_models())
        return

        # await llm_client.system.list_downloaded_models()

        # TODO: for some reason the code will hang unless you edit this line
        print("sdfaSs")

        # result = await llm_client.getLoadConfig(model_path)
        # model = await llm_client.llm.get("qwen2")
        # signal = AbortSignal()
        # try:
        #    model = await (
        #        await llm_client.llm.load(
        #            "lmstudio-community/Qwen2-500M-Instruct-GGUF", {"config": {"context_length": 1000}}
        #        )
        #    )
        # except Exception as e:
        #    print("Failed to load model:", e)

        model = await llm_client.llm.get("qwen2")
        # print("sleeping")
        # await asyncio.sleep(1)
        # await signal.abort()
        # print("should be aborted")
        # raise Exception("Test")
        # model = await model
        # print("Model loaded:", model)
        # raise Exception("Test")
        # TODO unasyncify this

        result = await model.respond([{"role": "user", "content": "Tell me a long story."}], {})
        print("Result:", result)
        print(await result)
        # result = await (await model.respond([{"role": "user", "content": "Say only the word 'hi'."}], {}))
        # async for completion in result:
        #    print(type(completion))
        #    print("frag", completion)
        # TODO result does not properly close
        # return
        print(type(result))
        # result = await llm_client.load_model(model_path)
        print("Model loaded:", result)

        tokenCount = await model.unstable_tokenize("Hello, how are you?")
        print("Token count:", tokenCount)

        contextLength = await model.unstable_get_context_length()
        print("Context length:", contextLength)

        # async for completion in llm_client.predict(model_path):
        #    print(completion)
    # except Exception as e:
    # print("Error:", e)
    finally:
        # pass
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

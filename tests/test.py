from lmstudio_sdk.LMStudioClient import LMStudioClient


async def main():
    # TODO: your errors are indented
    llm_client = await LMStudioClient.create({"base_url": "ws://localhost:1234"})
    try:
        # model_path = "lmstudio-community/gemma-2-2b-it-GGUF/gemma-2-2b-it-Q8_0.gguf"
        # model_path = "Qwen/Qwen2-0.5B-Instruct-GGUF/qwen2-0_5b-instruct-q4_0.gguf"
        # model_path = "qwen2"

        # result = await llm_client.getLoadConfig(model_path)
        model = await llm_client.llm.unstable_get_any()
        # TODO unasyncify this
        result = model.respond([{"role": "user", "content": "Hello, how are you?"}], {})
        async for completion in result:
            print(type(completion))
            print("frag", completion)
        # TODO result does not properly close
        print(type(result))
        # result = await llm_client.load_model(model_path)
        print("Model loaded:", result)

        # async for completion in llm_client.predict(model_path):
        #    print(completion)
    finally:
        await llm_client.close()


def syncmain():
    llm_client = LMStudioClient({"base_url": "ws://localhost:1234"})
    try:
        model = llm_client.llm.unstable_get_any()
        result = model.respond([{"role": "user", "content": "Hello, how are you?"}], {})
        print(result)
        for completion in result:
            print(type(completion))
            print("frag", completion)
    finally:
        llm_client.close()


if __name__ == "__main__":
    syncmain()
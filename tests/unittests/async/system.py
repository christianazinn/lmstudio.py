import unittest
from lmstudio_sdk import LMStudioClient


class TestSystem(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        # TODO: remove base URL
        self.client = await LMStudioClient(base_url="ws://localhost:1234")

    async def test_create_invalid_client_with_bad_scheme(self) -> None:
        with self.assertRaises(ValueError):
            await LMStudioClient(base_url="http://localhost:1234")

    async def test_create_invalid_client_with_bad_query(self) -> None:
        with self.assertRaises(ValueError):
            await LMStudioClient(base_url="ws://localhost:1234?query=1234")

    async def test_create_invalid_client_with_bad_fragment(self) -> None:
        with self.assertRaises(ValueError):
            await LMStudioClient(base_url="ws://localhost:1234#fragment")

    async def test_create_invalid_client_with_bad_username(self) -> None:
        with self.assertRaises(ValueError):
            await LMStudioClient(base_url="ws://username@localhost:1234")

    async def test_create_invalid_client_with_bad_password(self) -> None:
        with self.assertRaises(ValueError):
            await LMStudioClient(base_url="ws://username:password@localhost:1234")

    async def test_create_invalid_client_with_bad_trailing_slash(self) -> None:
        with self.assertRaises(ValueError):
            await LMStudioClient(base_url="ws://localhost:1234/")

    async def test_create_invalid_client_with_bad_url(self) -> None:
        with self.assertRaises(ValueError):
            await LMStudioClient(base_url="ws://localhost:019234")

    async def test_list_downloaded_models(self) -> None:
        result = await self.client.system.list_downloaded_models()
        self.assertIsInstance(result, list)

    async def asyncTearDown(self) -> None:
        await self.client.close()

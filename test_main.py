import pytest
from httpx import AsyncClient

import main

pytestmark = pytest.mark.anyio(anyio_backend='asyncio')


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
def client() -> AsyncClient:
    return AsyncClient(app=main.app, base_url='http://test')


async def test_info(client: AsyncClient):
    async with client:
        response = await client.get('/info')

    assert response.status_code == 200
    assert response.json() == {'Receiver': 'Cisco is the best!'}


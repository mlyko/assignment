import asyncio

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import main

pytestmark = pytest.mark.anyio(anyio_backend='asyncio')


fake_app = FastAPI()

@fake_app.get('/html')
async def handle_html():
    return HTMLResponse('<html><body/></html>')


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
def client() -> AsyncClient:
    main.app.extra['ping_timeout'] = 1.0
    main.app.extra['test_config'] = {
        'app': fake_app
    }
    return AsyncClient(app=main.app, base_url='http://test')


async def test_info(client: AsyncClient):
    async with client:
        response = await client.get('/info')

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/json'
    assert response.json() == {'Receiver': 'Cisco is the best!'}


async def test_ping(client: AsyncClient):
    async with client:
        response = await client.post('/ping', json={
            'url': 'http://fake/html'
        })

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'text/html; charset=utf-8'
    assert response.text == '<html><body/></html>'


async def test_ping_error(client: AsyncClient):
    async with client:
        response = await client.post('/ping', json={
            'url': 'http://fake/error'
        })

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/json'
    assert response.json() == {
        'status': 400,
        'error': 'Not Found'
    }


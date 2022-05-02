import argparse

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel


class PingModel(BaseModel):
    url: str


app = FastAPI()


@app.post('/ping')
async def handle_ping(ping: PingModel):
    async with httpx.AsyncClient(verify=False, follow_redirects=1) as client:
        response: httpx.Response = await client.get(ping.url, timeout=10.0)

    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        return Response(response.content, status_code=200, media_type=content_type)

    status_code = 400 if 400 <= response.status_code < 500 else 500
    return JSONResponse({
        'status': status_code,
        'error': response.reason_phrase
    }, status_code=status_code)


@app.get('/info')
async def handle_info():
    return {'Receiver': 'Cisco is the best!'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host',
                        help='TCP/IP hostname to serve on (default: %(default)r)',
                        default='localhost')
    parser.add_argument('-P', '--port',
                        help='TCP/IP port to serve on (default: %(default)r)',
                        type=int, default='8080')
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level='info')

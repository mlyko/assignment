#!/usr/bin/python3

"""A simple WEB application that handles two types of HTTP requests:
  * /ping - POST requests accepting a JSON body containing a url key and
    corresponding link. It sends a GET request to a received link and returns
    a payload of that GET request
  * /info - GET requests returning a hardcoded JSON response
"""

__author__ = 'Marcin Łyko'
__email__ = 'marcin.g.lyko@gmail.com'

import copy
import logging
import argparse

import httpx
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel


class PingModel(BaseModel):
    url: str


app = FastAPI()
logger = logging.getLogger('assignment')


@app.post('/ping')
async def handle_ping(ping: PingModel) -> Response:
    """
    Handles ping POST requests accepting a link in a JSON body.
    """
    logger.info('Handle ping request: %s', ping.url)
    async with httpx.AsyncClient(verify=False, follow_redirects=1) as client:
        try:
            response: httpx.Response = await client.get(ping.url, timeout=10.0)
        except httpx.ConnectError as err:
            logger.error('Ping request connection error: %s, error=%s', ping.url, err)
            return JSONResponse({
                'status': 502,
                'error': str(err)
            }, status_code=502)
        except httpx.ReadTimeout:
            logger.error('Ping request timeout: %s', ping.url)
            return JSONResponse({
                'status': 504,
                'error': 'Timeout'
            }, status_code=504)

    if response.status_code == 200:
        # Return payload when the GET request was succeed
        content_type = response.headers.get('Content-Type')
        return Response(response.content, status_code=200, media_type=content_type)

    logger.warning('Ping request failed: %d %s',
                   response.status_code, response.reason_phrase)
    status_code = 400 if 400 <= response.status_code < 500 else 500
    return JSONResponse({
        'status': status_code,
        'error': response.reason_phrase
    }, status_code=status_code)


@app.get('/info')
async def handle_info() -> dict:
    """
    Handles info GET requests returning a hardcoded JSON body.
    """
    logger.info('Handle info request')
    return {'Receiver': 'Cisco is the best!'}


def configure_logging(log_level: int):
    log_format = '%(asctime)s - %(levelname)s : %(message)s'

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)
    logger.setLevel(log_level)

    log_config = copy.deepcopy(LOGGING_CONFIG)
    log_config['formatters']['default']['fmt'] = log_format
    access_format = '%(asctime)s - %(levelname)s %(client_addr)s : "%(request_line)s" %(status_code)s'
    log_config['formatters']['access']['fmt'] = access_format

    return log_config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='turn on the debug mode')
    parser.add_argument('-H', '--host',
                        help='TCP/IP hostname to serve on (default: %(default)r)',
                        default='localhost')
    parser.add_argument('-P', '--port',
                        help='TCP/IP port to serve on (default: %(default)r)',
                        type=int, default='8080')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    log_config = configure_logging(log_level)
    uvicorn.run(app, host=args.host, port=args.port,
                log_level=log_level, log_config=log_config)

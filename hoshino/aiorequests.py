import asyncio
from functools import partial
from typing import Optional, Any

import requests
from requests import *


async def run_sync_func(func, *args, **kwargs) -> Any:
    return await asyncio.get_event_loop().run_in_executor(
        None, partial(func, *args, **kwargs))


class AsyncResponse:
    def __init__(self, response: requests.Response):
        self.raw_response = response

    @property
    def ok(self) -> bool:
        return self.raw_response.ok
    
    @property
    def status_code(self) -> int:
        return self.status_code

    def __repr__(self):
        return '<AsyncResponse [%s]>' % self.raw_response.status_code

    def __bool__(self):
        return self.ok

    @property
    async def content(self) -> Optional[bytes]:
        return await run_sync_func(lambda: self.raw_response.content)

    @property
    async def text(self) -> str:
        return await run_sync_func(lambda: self.raw_response.text)

    async def json(self, **kwargs) -> Any:
        return await run_sync_func(self.raw_response.json, **kwargs)


async def request(method, url, **kwargs) -> AsyncResponse:
    return AsyncResponse(await run_sync_func(requests.request,
                                             method=method, url=url, **kwargs))


async def get(url, params=None, **kwargs) -> AsyncResponse:
    return AsyncResponse(
        await run_sync_func(requests.get, url=url, params=params, **kwargs))


async def options(url, **kwargs) -> AsyncResponse:
    return AsyncResponse(
        await run_sync_func(requests.options, url=url, **kwargs))


async def head(url, **kwargs) -> AsyncResponse:
    return AsyncResponse(await run_sync_func(requests.head, url=url, **kwargs))


async def post(url, data=None, json=None, **kwargs) -> AsyncResponse:
    return AsyncResponse(await run_sync_func(requests.post, url=url,
                                             data=data, json=json, **kwargs))


async def put(url, data=None, **kwargs) -> AsyncResponse:
    return AsyncResponse(
        await run_sync_func(requests.put, url=url, data=data, **kwargs))


async def patch(url, data=None, **kwargs) -> AsyncResponse:
    return AsyncResponse(
        await run_sync_func(requests.patch, url=url, data=data, **kwargs))


async def delete(url, **kwargs) -> AsyncResponse:
    return AsyncResponse(
        await run_sync_func(requests.delete, url=url, **kwargs))

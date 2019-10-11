# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Provide a RESTlike interface to manage the ControlPeer remotely"""

import asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from uvicorn import Server, Config

from .flows import create_flow_router


class HelloWorld(BaseModel):  # pylint: disable=too-few-public-methods
    message: str = "Hello, World!"


class WebApi:
    """Provide a RESTlike interface to manage the ControlPeer remotely

    Arguments:
        control_peer (ControlPeer): an instance of the ControlPeer

    Usage:
        create an Instance of the WebAPI (glued together with FastAPI/Starlette and uvicorn)
        and use `run` to create an endlessly running asyncio task
        or use the `serve` coroutine to run it manually
    """
    def __init__(self, control_peer):
        self.server = None
        self.server_task = None

        self.api = FastAPI(
            title="Titan ControlPeer WebApi",
            version="1.0",
            description="A RESTlike interface to manage the ControlPeer remotely",
        )

        self.api.get('/hello', response_model=HelloWorld)(self.hello)

        flow_router = create_flow_router(control_peer)
        self.api.router.include_router(flow_router, prefix="/api/v1/flows", tags=["Flows"])

    def run(self):
        """Create an endlessly running server-task and schedule it in the current event loop"""
        self.server_task = asyncio.create_task(self.serve())

    async def stop(self):
        self.server_task.cancel()
        self.server.should_exit = True
        await self.server.shutdown()

    async def serve(self):
        """serve the api using uvicorn"""
        config = Config(self.api)
        self.server = Server(config=config)

        # we will handle Ctrl+C/Sigterm ourselves. thank you.
        self.server.install_signal_handlers = lambda: None

        await self.server.serve()

    @staticmethod
    def hello():
        """Get a message: `Hello, World!`"""
        return HelloWorld()

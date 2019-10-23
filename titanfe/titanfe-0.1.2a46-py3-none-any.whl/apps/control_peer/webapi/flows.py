# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Routes for Flow management"""
from enum import Enum
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel


# Constants
class StateName(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# Response Types
class FlowResponse(BaseModel):  # pylint: disable=too-few-public-methods
    name: str
    uid: str
    state: str


# Request Parameter
class RequestStateChange(BaseModel):  # pylint: disable=too-few-public-methods
    state: StateName


# Routes
def create_flow_router(control_peer):
    """Setup the routing for flow management

    Arguments:
        control_peer (ControlPeer): an instance of the ControlPeer

    Returns:
        APIRouter: router/routes to manage the control peer's flows
    """
    router = APIRouter()

    @router.get("/", response_model=List[FlowResponse])
    def list_flows():  # pylint: disable=unused-variable
        """List the currently configured flows and their state"""
        flows = [
            FlowResponse(name=flow.name, uid=flow.uid, state=flow.state.name)
            for flow in control_peer.flows
        ]
        return flows

    @router.put("/{flow_uid}", response_model=FlowResponse)
    async def change_flow_state(  # pylint: disable=unused-variable
            flow_uid: str, request: RequestStateChange
    ):
        if request.state == StateName.INACTIVE:
            flow = await control_peer.stop_flow(flow_uid)

        if request.state == StateName.ACTIVE:
            flow = control_peer.start_flow(flow_uid)

        return FlowResponse(name=flow.name, uid=flow.uid, state=flow.state.name)

    return router

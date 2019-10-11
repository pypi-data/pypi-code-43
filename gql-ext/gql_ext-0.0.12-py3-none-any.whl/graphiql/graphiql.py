import json
import os
from functools import partial
from string import Template
from typing import Optional, Dict, Any, List

from aiohttp import web
from aiohttp.web import Application
from aiohttp.web_response import Response

__all__ = ('set_graphiql_handler',)

with open(os.path.join(os.path.dirname(__file__), 'graphiql.html')) as tpl_file:
    _GRAPHIQL_TEMPLATE = tpl_file.read()


def set_graphiql_handler(
        app: Application,
        graphiql_enabled: bool,
        graphiql_options: Optional[Dict[str, Any]],
        executor_http_endpoint: str,
        executor_http_methods: List[str],
        subscription_ws_endpoint: Optional[str],
) -> None:
    if not graphiql_enabled:
        return

    if graphiql_options is None:
        graphiql_options = {}

    app.router.add_route(
        "GET",
        graphiql_options.get("endpoint", "/graphiql"),
        partial(
            graphiql_handler,
            graphiql_options={
                "endpoint": executor_http_endpoint,
                "is_subscription_enabled": json.dumps(
                    bool(subscription_ws_endpoint)
                ),
                "subscription_ws_endpoint": subscription_ws_endpoint,
                "query": graphiql_options.get("default_query") or "",
                "variables": validate_and_compute_graphiql_option(
                    graphiql_options.get("default_variables"),
                    "default_variables",
                    "",
                    2,
                ),
                "headers": validate_and_compute_graphiql_option(
                    graphiql_options.get("default_headers"),
                    "default_headers",
                    "{}",
                ),
                "http_method": "POST"
                if "POST" in executor_http_methods
                else "GET",
            },
        ),
    )


def validate_and_compute_graphiql_option(
        raw_value: Any, option_name: str, default_value: str, indent: int = 0
) -> str:
    if not raw_value:
        return default_value

    if not isinstance(raw_value, dict):
        raise TypeError(
            f"< graphiql_options.{option_name} > parameter should be a dict."
        )

    try:
        return json.dumps(raw_value, indent=indent)
    except Exception as e:
        raise ValueError(
            f"Unable to jsonify < graphiql_options.{option_name} value. "
            f"Error: {e}."
        )


async def graphiql_handler(request, graphiql_options: Dict[str, Any]) -> Response:
    return web.Response(
        text=_render_graphiql(graphiql_options),
        headers={"Content-Type": "text/html"},
    )


def _render_graphiql(graphiql_options: Dict[str, Any]) -> str:
    return Template(_GRAPHIQL_TEMPLATE).substitute(
        endpoint=graphiql_options["endpoint"],
        is_subscription_enabled=graphiql_options["is_subscription_enabled"],
        subscription_ws_endpoint=graphiql_options["subscription_ws_endpoint"],
        http_method=graphiql_options["http_method"],
        default_query=graphiql_options["query"],
        default_variables=graphiql_options["variables"],
        default_headers=graphiql_options["headers"],
    )

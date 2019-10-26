import logging
import uvicorn

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from middleware import RequestIDMiddleware, get_request_id

logger = logging.getLogger("gunicorn.error")
app = Starlette()


@app.route("/")
def homepage(request):
    logger.info(f"Request ID: {get_request_id()}")
    return PlainTextResponse("hello world")


app.add_middleware(
    RequestIDMiddleware,
    prefix="mooo-"
)

if __name__ == "__main__":
    uvicorn.run(app)

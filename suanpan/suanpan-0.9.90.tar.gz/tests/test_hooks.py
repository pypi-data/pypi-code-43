import suanpan
from suanpan.app import app
from suanpan.arguments import String


@app.output(String(key="outputData1"))
def test_app(_):
    print("test_app")
    return "test_app"


@app.beforeInit
def test_app_before_init():
    print("app_before_init")


@app.afterInit
def test_app_after_init(_):
    print("app_after_init")


@app.beforeCall
def test_app_before_call(_):
    print("app_before_call")


@app.afterCall
def test_app_after_call(_):
    print("app_after_call")


@app.beforeExit
def test_app_before_exit(_):
    print("app_before_exit")


@app.trigger(interval=1)
@app.trigger.output(String(key="outputData1"))
def test_trigger(_):
    print("test_trigger")
    return "test_trigger"


@app.trigger.beforeInit
def test_trigger_before_init():
    print("trigger_before_init")


@app.trigger.afterInit
def test_trigger_after_init(_):
    print("trigger_after_init")


@app.trigger.beforeCall
def test_trigger_before_call(_):
    print("trigger_before_call")


@app.trigger.afterCall
def test_trigger_after_call(_):
    print("trigger_after_call")


@app.trigger.beforeExit
def test_trigger_before_exit(_):
    print("trigger_before_exit")


if __name__ == "__main__":
    suanpan.run(app)

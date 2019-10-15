import suanpan
from suanpan.app import app


@app.trigger(loop=range(10000))
def test_loop_iterable(_, i):
    print(i)


if __name__ == "__main__":
    suanpan.run(app)

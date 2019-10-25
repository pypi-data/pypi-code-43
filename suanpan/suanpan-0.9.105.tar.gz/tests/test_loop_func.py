import time
import random
import suanpan
from suanpan.app import app


def test_generator():
    for i in range(10000000000):
        yield i
        time.sleep(random.randint(0, 5))


@app.trigger(loop=test_generator)
def test2(_, i):
    print(i)


if __name__ == "__main__":
    suanpan.run(app)

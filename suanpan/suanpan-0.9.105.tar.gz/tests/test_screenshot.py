import suanpan
from suanpan.app import app
from suanpan.app.arguments import String
from suanpan.screenshots import screenshots
from suanpan.utils import image

test_image = image.read("tests/test.png")


@app.afterInit
def clean_screenshots(_):
    screenshots.clean()


@app.param(String(key="param1"))
def test_screenshots(_):
    for _ in range(10):
        screenshots.save(test_image)


if __name__ == "__main__":
    suanpan.run(app)

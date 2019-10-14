import argparse
import os
import shutil
import tempfile
import time
import requests
import json
import uuid
from PIL import Image
from selenium.common.exceptions import JavascriptException

# 0 = Manually define each baseline,  1 = Assisted baseline management, 2 = Force non
# existent baselines, 3 Overwrite all baselines
MANUAL, ASSISTED, FORCE_NEW, FORCE_ALL = 0, 1, 2, 3
# 0 = Pixel diff, 1 = Ignore Aliasing, 2= Ignore color 3= layout / Not implemented, 4= detect errors
PIXEL_DIFF, IGNORE_AA, IGNORE_COLOR, DETECT_ERRORS = 0, 1, 2, 3

_dir = tempfile.mkdtemp()
module_comparison_logic = 1
module_baseline_management = 1
_execution_id = None
module_api_key = None
module_api_secret_key = None
module_app_id = None
viewport_width = None
viewport_height = None
base_url = "https://us-central1-lince-232621.cloudfunctions.net/"
_report_base_url = "https://www.oculow.com/dashboard/executions.html"
execution_status_function = "get_execution_status-prod"  # TODO extract to config file
process_function = "process_image-prod"  # TODO extract to config file


def get_result():
    url = base_url + execution_status_function
    r = requests.post(url, data={
        'api_key': module_api_key,
        'app_id': module_app_id,
        'execution_id': _execution_id
    })
    print(r)
    print(r.json())
    return r.json()


def upload_image(image):
    global _execution_id
    url = base_url + process_function
    files = {'file': open(image, 'rb')}
    r = requests.post(url, files=files, data={
        'api_key': module_api_key + "__" + module_secret_key,
        'app_id': module_app_id,
        'comparison_logic': module_comparison_logic,
        'execution_id': _execution_id,
        'baseline_management': module_baseline_management,

        "viewport": json.dumps({"width": viewport_width, "height": viewport_height})
    })
    print(r)
    r_response = r.json()
    print(r_response)
    if not _execution_id:
        _execution_id = r_response['execution_id'] if 'execution_id' in r_response else r_response
    print("Uploaded image {}\n".format(image))


def capture_screen(driver, title=None):
    """

    :param driver: Selenium driver used in automation.
    :param title: title to set the image. If none is specified, it will retrieve the websites title.
    :param duplicate_header: if there are floating headers, this will force it to absolute position.
    :return: Returns the final title of the image.
    """
    if not title:
        title = driver.title
    save_path = os.path.join(_dir, title)
    name, ext = os.path.splitext(save_path)
    if not ext or ext.lower() != 'png':
        save_path = save_path + ".png"
    take_visible_screenshot(driver, save_path)

    upload_image(save_path)
    # _upload_image("C:/Users/Potosin/Desktop/test_images/Capture2.png")

    return title


def take_visible_screenshot(driver, file):
    global viewport_height, viewport_width
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    driver.get_screenshot_as_file(file)
    return True


def _fullpage_screenshot(driver, file):
    global viewport_height, viewport_width
    # Method pulled from github post https://stackoverflow.com/questions/41721734/take-screenshot-of-full-page-with-selenium-python-with-chromedriver
    print("Starting chrome full page screenshot workaround ...")

    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height, viewport_width, viewport_height))
    rectangles = []

    # Pad verticall scroll to deal with floating headers
    scroll_pad = 200

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            print("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
            rectangles.append((ii, i, top_width, top_height))

            ii = ii + viewport_width

        i = i + viewport_height - scroll_pad

    stitched_image = Image.new('RGB', (total_width, total_height - scroll_pad))
    previous = None
    part = 0

    for rectangle in rectangles:
        if not previous is None:
            try:
                driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            except JavascriptException:
                driver.execute_script(
                    "document.body.scrollTop = 0;")  # TODO implement logic for apptim similar website.
            print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.2)

        file_name = "part_{0}.png".format(part)
        print("Capturing {0} ...".format(file_name))

        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            # We know that the first time the image was not cropped, we don't modify the offset.
            offset = (rectangle[0], rectangle[1] + scroll_pad if rectangle[1] > 0 else 0)

        print("Adding to stitched image with offset ({0}, {1})".format(offset[0], offset[1]))
        if offset[1] > 0:
            w, h = screenshot.size
            screenshot = screenshot.crop((0, scroll_pad, w, h))
        stitched_image.paste(screenshot, offset)

        del screenshot
        os.remove(file_name)
        part = part + 1
        previous = rectangle

    stitched_image.save(file)
    print("Finishing chrome full page screenshot workaround...")
    return True


def dispose():
    """
    Makes sure to remove any temporary files created during execution.
    :return:
    """
    results = get_result()
    shutil.rmtree(_dir)
    if str(results).lower() == "action required":
        print("Baseline action is required, visit {}?id={}".format(
            _report_base_url, _execution_id))
    elif str(results).lower() == "failed":
        print("Tests failed, please review at {}?id={}".format(
            _report_base_url, _execution_id))
    assert (str(results) == "passed")

    print("To view a detailed report of the execution please navigate to {}?id={}".format(
        _report_base_url, _execution_id))


def set_api_key(api_key, secret_key):
    global module_api_key, module_secret_key
    module_api_key = api_key
    module_secret_key = secret_key


def set_comparison_logic(comparison_logic):
    global module_comparison_logic
    module_comparison_logic = comparison_logic


def set_app_id(app_id):
    global module_app_id
    module_app_id = app_id


def set_baseline_management(baseline_management):
    global module_baseline_management
    module_baseline_management = baseline_management

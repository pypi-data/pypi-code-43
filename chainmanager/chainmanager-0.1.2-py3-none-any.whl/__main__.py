import eel
import os

from chainmanager.model.manager import Manager, ExcelKeyError
from chainmanager.form import *
from chainmanager.ui.file_chooser import FileChooser
from pathlib import Path
from selenium import webdriver
import hashlib

manager = Manager()

security_password = False


def check_password_signed():
    global security_password
    if security_password is False:
        eel.close_window()
        return

@eel.expose
def check_password(password):
    global security_password
    if (hashlib.sha256(str.encode(password)).hexdigest() ==
            '830e0d1c621a94b7c3b7495f1323c25ae516c8eaf5a486949514599d1d1472d6'):
        security_password = True
        return True
    else:
        security_password = False
        return False


@eel.expose
def send_credentials(username, password):
    check_password_signed()
    manager.username = username
    manager.password = password
    # TODO Check if values given are right values for its content (XE.... or E...)


@eel.expose
def ask_file(file_type, original_path):
    """ Ask the user to select a file """
    check_password_signed()
    return FileChooser().open_dialog(file_type, original_path)


@eel.expose
def load_data(path):
    check_password_signed()
    if not Path(path).is_file():
        eel.show_warning(f"There is not excel file on {path}")
        return -1

    try:
        manager.read_from_excel(path)
    except ExcelKeyError as e:
        eel.show_warning(e.message)
        return -1

    return len(manager.chain_names())


@eel.expose
def chain_names():
    check_password_signed()
    return manager.chain_names()


@eel.expose
def job_names(chain):
    check_password_signed()
    return manager.job_names(chain)


@eel.expose
def write_data(data):
    check_password_signed()
    chains = manager.get_chains(data)
    if len(chains) == 0:
        return
    driver = webdriver.Firefox()
    mainmenu = MainMenuClass(driver, manager.username, manager.password)
    mainmenu.start()
    mainmenu.sign_in()

    main_controller = MainController(mainmenu)
    main_controller.write_chains(chains)

    driver.close()


def run():
    web_location = 'web'
    web_path = os.path.dirname(os.path.realpath(__file__)) + '/' + web_location
    eel.init(web_path)

    try:
        chrome_instance_path = eel.chrome.get_instance_path()
        if chrome_instance_path is not None and os.path.exists(chrome_instance_path):
            eel.start('main.html', size=(850, 900), options={'port': 0})
        else:
            eel.start('main.html', size=(850, 900), options={'port': 0, 'mode': 'user selection'})
    except (SystemExit, KeyboardInterrupt):
        pass


if __name__ == '__main__':
    run()

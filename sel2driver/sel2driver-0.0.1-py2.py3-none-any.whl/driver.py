from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeDriverManager
from webdriver_manager.microsoft import IEDriverManager
from selenium import webdriver


def browserDriver(browser):
    if browser == 'firefox':
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        driver.maximize_window()
        driver.implicitly_wait(10)

    elif browser == 'edge':
        driver = webdriver.Edge(executable_path=EdgeDriverManager().install())
        driver.maximize_window()
        driver.implicitly_wait(10)

    elif browser == 'ie':
        driver = webdriver.Ie(executable_path=IEDriverManager().install())
        driver.maximize_window()
        driver.implicitly_wait(10)

    else:
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        driver.maximize_window()
        driver.implicitly_wait(10)

    return driver

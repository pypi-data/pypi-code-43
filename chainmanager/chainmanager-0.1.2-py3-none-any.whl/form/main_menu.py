from .form_utils import *
from .chain_form import ChainNewForm, ChainSearchForm
from .job_form import JobNewForm, JobSearchForm


class MainMenuClass:
    def __init__(self, driver, user, password):
        self.driver = driver
        self.user = user
        self.password = password

    def start(self):
        self.driver.get("https://e-spacio.es.igrupobbva/WebGestDoc/")
        wait_until_loaded(self.driver, name="username", delay=1000)

    def sign_in(self):
        fill_input(self.driver, self.user, name="username")
        fill_input(self.driver, self.password, name="password")
        key_intro(self.driver, identifier="accept")
        wait_until_loaded(self.driver, identifier="contentImagenes", delay=1000)

    def index(self):
        try:
            wait_until_loaded(self.driver, css=".glyphicon-home", delay=1)
            self.home()
        except TimeoutException:
            self.driver.get("https://e-spacio.es.igrupobbva/WebGestDoc/")
        # TODO Comprobar si existe botón inicio, de estamanera nos ahorramos la carga completa de la página
        wait_until_loaded(self.driver, identifier="contentImagenes", delay=1000)

    def chain_search(self):
        self.index()
        self.chains()
        self.search()

        chainform = ChainSearchForm(self.driver)
        chainform.is_ready(delay=1000)
        return chainform

    def chain_new(self):
        self.index()
        self.chains()
        self.new()

        chainform = ChainNewForm(self.driver)
        chainform.is_ready(delay=1000)
        return chainform

    def job_search(self):
        self.index()
        self.jobs()
        self.search()

        jobform = JobSearchForm(self.driver)
        jobform.is_ready(delay=1000)
        return jobform

    def job_new(self):
        self.index()
        self.jobs()
        self.new()

        jobform = JobNewForm(self.driver)
        jobform.is_ready(delay=1000)
        return jobform

    def chains(self):
        self._click_main_menu("cadenas")

    def jobs(self):
        self._click_main_menu("jobs")

    def search(self):
        self._click_main_menu("operaciones")

    def new(self):
        self._click_main_menu("alta")

    def _click_main_menu(self, option):
        identifier, img = None, None
        if option == "cadenas":
            (identifier, img) = ("contentImagenes", "CADENAS")
        if option == "jobs":
            (identifier, img) = ("contentImagenes", "JOBS")
        if option == "operaciones":
            (identifier, img) = ("operativas", "OPERACIONES")
        if option == "alta":
            (identifier, img) = ("operativas", "ALTA DE INFORMACION")

        elem = get_child_tags(self.driver.find_element_by_id(identifier), "div")
        self._click_main_menu_img(elem, img)

    def _click_main_menu_img(self, elems, text):
        img = None
        for elem in elems:
            if text in elem.text:
                img = elem.find_element_by_tag_name("img")
        img.click()

    def back(self):
        self._click_menu_option_icon("glyphicon-menu-left")

    def home(self):
        self._click_menu_option_icon("glyphicon-home")

    def _click_menu_option_icon(self, icon_class):
        menu_option = None
        top_menu_buttons = self.driver.find_elements_by_class_name("mini-circular")
        for button in top_menu_buttons:
            icon = button.find_element_by_tag_name("span")
            if icon_class in icon.get_attribute("class"):
                menu_option = button
        menu_option.click()

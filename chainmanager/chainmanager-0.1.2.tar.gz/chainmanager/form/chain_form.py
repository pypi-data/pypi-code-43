from .form_utils import *


class ChainNewForm:

    def __init__(self, driver):
        self.driver = driver

    def fill_form(self, chain):
        self.fill_chain(chain)
        self.fill_dependencies(chain)

    def send_form(self):
        click(self.driver, identifier="frmAltaBtnOK")
        wait_until_alert(self.driver)
        self.driver.switch_to.alert.accept()

    def fill_chain(self, chain):
        fill_input(self.driver, chain.document, name="des_refdocum")
        fill_input(self.driver, chain.chain, name="des_cadenapl")
        self.driver.execute_script('$("#cod_aplicaci").removeAttr("readonly")')
        fill_input(self.driver, chain.uuaa, name="cod_aplicaci")
        fill_input(self.driver, chain.author, name="des_autor")
        fill_input(self.driver, chain.modification, name="fec_modifica")
        fill_input(self.driver, chain.description, name="des_descaden")

        fill_input(self.driver, chain.team, name="des_equipocd")
        fill_select(self.driver, chain.periodicity, name="xti_periocdn")
        fill_input(self.driver, chain.execution_day, name="des_diaejecu")
        fill_input(self.driver, chain.time, name="des_horaejec")
        self.driver.execute_script('$("#xti_critical").removeAttr("readonly")')
        fill_select(self.driver, chain.criticality, name="xti_critical")
        self.driver.execute_script('$("#des_rearran").removeAttr("readonly")')
        fill_input(self.driver, chain.reruns, name="des_rearran")
        fill_input(self.driver, chain.interrelation_online, name="des_interrel")

        fill_input(self.driver, chain.incompatibilities, name="des_incompat")

    def fill_dependencies(self, chain):
        self.clear_dependencies()
        for dependency in chain.dependencies:
            self.fill_dependencia(dependency)

    def fill_dependencia(self, dependencia):
        self.driver.find_element_by_link_text("Crear nueva relación +").click()

        item = find_element(self.driver, css="#cdnRelaciones tbody tr:last-child")

        fill_input(item, dependencia.script_name, name="des_scriptjb")
        fill_input(item, dependencia.script_pre, name="des_scriptpr")
        fill_input(item, dependencia.chain_pre, name="des_cadenapd")
        fill_input(item, dependencia.script_post, name="des_scriptsu")
        fill_input(item, dependencia.chain_post, name="des_cadenasu")



    def clear_dependencies(self):
        elems = find_elements(self.driver, css=".btn.label.label-danger")
        for elem in elems:
            elem.click()

    def is_ready(self, delay=0):
        wait_until_loaded(self.driver, css=".titulo-form-alta", delay=delay)


class ChainSearchForm:
    def __init__(self, driver):
        self.driver = driver

    def clean_search_chain(self):
        click(self.driver, css="#fieldBusca button.pull-left")

    def search_chain(self, documento=None, cadena=None, autor=None, uuaa=None, borrador=False):
        self.clean_search_chain()
        if documento is not None:
            fill_input(self.driver, documento, identifier="des_refdocum")
        if cadena is not None:
            fill_input(self.driver, cadena, identifier="des_cadenapl")
        if autor is not None:
            fill_input(self.driver, autor, identifier="des_autor")
        if uuaa is not None:
            fill_input(self.driver, uuaa, identifier="cod_aplicaci")

        borrador_css = "#busca_xti_borrado[value='S']" if borrador else "#busca_xti_borrado[value='N']"
        click(self.driver, css=borrador_css)
        click(self.driver, css="#fieldBusca button.pull-right")
        wait_until_loaded(self.driver, css="ngx-datatable", delay=1000)

    def search_all_chains(self, documento=None, cadena=None, autor=None, uuaa=None, borrador=False):
        documento = "*" + documento + "*" if documento is not None else documento
        cadena = "*" + cadena + "*" if cadena is not None else cadena
        autor = "*" + autor + "*" if autor is not None else autor
        uuaa = "*" + uuaa + "*" if uuaa is not None else uuaa

        self.search_chain(documento, cadena, autor, uuaa, borrador)

    def chain_exists(self, documento=None, cadena=None, autor=None, uuaa=None, borrador=False):
        # TODO añadir un parametro que sea all or not all
        return self.chain_count(documento, cadena, autor, uuaa, borrador) != 0

    def chain_count(self, documento=None, cadena=None, autor=None, uuaa=None, borrador=False):
        self.search_all_chains(documento, cadena, autor, uuaa, borrador)

        return len(find_elements(self.driver, css="ngx-datatable datatable-body datatable-row-wrapper"))

    def view_chain(self, documento=None, cadena=None, autor=None, uuaa=None, borrador=False):
        if not self.chain_exists(documento, cadena, autor, uuaa, borrador):
            raise ValueError("There is not chain with that info")
        remove_element(self.driver, "#loaderPage")
        click(self.driver, css=".color-iconos.glyphicon.glyphicon-eye-open")

    def edit_chain(self, documento=None, cadena=None, autor=None, uuaa=None, borrador=False):
        if not self.chain_exists(documento, cadena, autor, uuaa, borrador):
            raise ValueError("There is not chain with that info")
        click(self.driver, css=".color-iconos.glyphicon.glyphicon-pencil")

        chainnewform = ChainNewForm(self.driver)
        chainnewform.is_ready(delay=1000)
        return chainnewform

    def remove_chain(self, documento=None, cadena=None, autor=None, uuaa=None, borrador=False):
        if not self.chain_exists(documento, cadena, autor, uuaa, borrador):
            raise ValueError("There is not chain with that info")
        click(self.driver, css=".color-iconos.glyphicon.glyphicon-trash")

    def is_ready(self, delay=0):
        wait_until_loaded(self.driver, identifier="areaBusca", delay=delay)

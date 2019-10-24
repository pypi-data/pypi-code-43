from .form_utils import *


class JobNewForm:

    def __init__(self, driver):
        self.driver = driver

    def fill_form(self, job):
        self.fill_job(job)
        self.fill_ficherosybbdd(job)
        self.fill_rearranques(job)
        self.fill_incompatibilidades(job)

    def send_form(self):
        click(self.driver, identifier="frmAltaBtnOK")
        wait_until_alert(self.driver)
        self.driver.switch_to.alert.accept()

    def fill_job(self, job):
        fill_input(self.driver, job.script, name="des_nombrjob")
        fill_input(self.driver, job.jobname, name="des_refdocjb")
        self.driver.execute_script('$("#cod_aplicaci").removeAttr("readonly")')
        fill_input(self.driver, job.uuaa, name="cod_aplicaci")

        self.driver.execute_script('$("#des_gsoporte").removeAttr("readonly")')
        fill_input(self.driver, job.support_group, name="des_gsoporte")

        fill_input(self.driver, job.origin_system, name="des_maqori")
        fill_input(self.driver, job.libreria_origen, name="des_libreori")
        fill_input(self.driver, job.description, name="des_desjobpl")
        fill_input(self.driver, job.periodicity, name="des_periojob")
        fill_input(self.driver, job.sub_application, name="des_estrupl")
        fill_input(self.driver, job.exectution_host, name="des_maqeje")
        fill_select(self.driver, job.criticality, name="xti_critijob")

        # TODO Introducir grupo de soporte

    def fill_ficherosybbdd(self, job):
        self.clear_ficherosybbdd()
        for fichero in job.filesanddb:
            self.fill_fichero(fichero)

    def fill_fichero(self, fichero):
        fieldset = find_elements(self.driver, css="#altaJobsForm fieldset")[1]
        fieldset.find_element_by_link_text("Crear nuevo paso +").click()

        item = find_element(self.driver, css="#jobsDescPasos tbody tr:last-child")

        fill_input(item, fichero.step, name="des_paso")
        fill_input(item, fichero.input, name="des_fichentr")
        fill_input(item, fichero.output, name="des_fichsali")
        fill_input(item, fichero.entities, name="des_entibd")
        fill_input(item, fichero.access_type, name="des_accesbd")

    def clear_ficherosybbdd(self):
        for elem in find_elements(self.driver, css="#jobsDescPasos .btn.label.label-danger"):
            elem.click()

    def fill_rearranques(self, job):
        self.clear_rearranques()
        for rearranque in job.reruns_rules:
            self.fill_rearranque(rearranque)

    def fill_rearranque(self, rearranque):
        fieldset = find_elements(self.driver, css="#altaJobsForm fieldset")[2]
        fieldset.find_element_by_link_text("Crear nuevo paso +").click()

        item = find_element(self.driver, css="#jobsRearranques tbody tr:last-child")

        fill_input(item, rearranque.step, css="[formcontrolname=des_paso]")
        fill_input(item, rearranque.before, css="[formcontrolname=des_predece]")
        fill_input(item, rearranque.after, css="[formcontrolname=des_sucesor]")
        fill_input(item, rearranque.reruns_rules, css="[formcontrolname=des_rearra]")

    def clear_rearranques(self):
        for elem in find_elements(self.driver, css="#jobsRearranques .btn.label.label-danger"):
            elem.click()

    def fill_incompatibilidades(self, job):
        self.clear_incompatibilidades()
        for incompatibilidad in job.incompatibilities:
            self.fill_incompatibilidad(incompatibilidad)

    def fill_incompatibilidad(self, incompatibilidad):
        fieldset = find_elements(self.driver, css="#altaJobsForm fieldset")[3]
        fieldset.find_element_by_link_text("Crear nuevo paso +").click()

        item = find_element(self.driver, css="#jobsIncompatibilidades tbody tr:last-child")

        fill_input(item, incompatibilidad.step, css="[formcontrolname=des_paso]")
        fill_input(item, incompatibilidad.incompatibilities, css="[formcontrolname=des_incomjob]")
        fill_select(item, incompatibilidad.criticality, css="[formcontrolname=xti_critinco]")

    def clear_incompatibilidades(self):
        for elem in find_elements(self.driver, css="#jobsIncompatibilidades .btn.label.label-danger"):
            elem.click()

    def is_ready(self, delay=0):
        wait_until_loaded(self.driver, css=".titulo-form-alta", delay=delay)


class JobSearchForm:
    def __init__(self, driver):
        self.driver = driver

    def clean_search_job(self):
        click(self.driver, css="#fieldBusca button.pull-left")

    def search_job(self, script=None, jobname=None, uuaa=None, borrador=False):
        self.clean_search_job()

        if script is not None:
            fill_input(self.driver, script, identifier="busca_des_nombrjob")
        if jobname is not None:
            fill_input(self.driver, jobname, identifier="busca_des_refdocjb")

        if uuaa is not None:
            fill_input(self.driver, uuaa, identifier="cod_aplicaci")

        borrador_css = "#busca_xti_borrado[value='S']" if borrador else "#busca_xti_borrado[value='N']"
        click(self.driver, css=borrador_css)
        click(self.driver, css="#frmBuscaJobBtnBusca")
        wait_until_loaded(self.driver, css="ngx-datatable", delay=1000)

    def search_all_jobs(self, script=None, jobname=None, uuaa=None, borrador=False):

        script = "*" + script + "*" if script is not None else script
        jobname = "*" + jobname + "*" if jobname is not None else jobname
        uuaa = "*" + uuaa + "*" if uuaa is not None else uuaa

        self.search_job(script, jobname, uuaa, borrador)

    def job_exists(self, script=None, jobname=None, uuaa=None, borrador=False):
        # TODO añadir un parametro que sea all or not all
        return self.job_count(script, jobname, uuaa, borrador) != 0

    def job_count(self, script=None, jobname=None, uuaa=None, borrador=False):
        self.search_all_jobs(script, jobname, uuaa, borrador)

        return len(find_elements(self.driver, css="ngx-datatable datatable-body datatable-row-wrapper"))

    def view_job(self, script=None, jobname=None, uuaa=None, borrador=False):
        if not self.job_exists(script, jobname, uuaa, borrador):
            raise ValueError("There is not job with that info")
        remove_element(self.driver, "#loaderPage")
        click(self.driver, css=".color-iconos.glyphicon.glyphicon-eye-open")

    def edit_job(self, script=None, jobname=None, uuaa=None, borrador=False):
        if not self.job_exists(script, jobname, uuaa, borrador):
            raise ValueError("There is not job with that info")
        remove_element(self.driver, "#loaderPage")
        click(self.driver, css=".color-iconos.glyphicon.glyphicon-pencil")

        jobnewform = JobNewForm(self.driver)
        jobnewform.is_ready(delay=1000)
        return jobnewform

    def remove_job(self, script=None, jobname=None, uuaa=None, borrador=False):
        if not self.job_exists(script, jobname, uuaa, borrador):
            raise ValueError("There is not job with that info")
        remove_element(self.driver, "#loaderPage")
        click(self.driver, css=".color-iconos.glyphicon.glyphicon-trash")

    def is_ready(self, delay=0):
        wait_until_loaded(self.driver, identifier="areaBusca", delay=delay)
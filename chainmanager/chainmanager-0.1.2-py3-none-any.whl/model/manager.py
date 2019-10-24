import pandas as pd
import numpy as np
from chainmanager.model import Chain, ChainDependency, Job, FileAndDb, Incompatibility, RerunRule


def split_rows(row, keys):
    matrix = [col.split("\n") for col in row[keys]]
    return pd.DataFrame(np.array(matrix).T,  columns=keys)


class ExcelKeyError(Exception):
    def __init__(self, message, sheet):
        super().__init__(message)
        self.message = message
        self.sheet = sheet

class Manager:
    def __init__(self):
        self.chains = []
        self.jobs = []
        self.path = None
        self.username = None
        self.password = None

    def clear_data(self):
        self.jobs = []
        self.chains = []
        self.path = ""

    def read_from_excel(self, path):
        self.clear_data()
        try:
            self._read_jobs(path)
            self._read_chains(path)
            self.path = path
        except ExcelKeyError as e:
            self.clear_data()
            raise e

    def _read_chains(self, path):
        sheet_names = pd.ExcelFile(path).sheet_names
        chain_names = [_ for _ in filter(lambda x: "mallas" in x, sheet_names)]
        for sheet in chain_names:
            self._read_chains_sheet(path, sheet)

    def _read_chains_sheet(self, path, sheet):

        print(sheet)

        CHAIN_MAIN_KEYS = ["documento", "cadena", "uuaa", "autor", "modificacion", "descripcion", "equipo",
                           "periodicidad", "ejecucion", "horario", "criticidad", "rearranques", "interrelacion",
                           "incompatibilidades"]
        CHAIN_DEPENDENCIES = ["nombre_script", "script_pre", "cadena_pre", "script_post", "cadena_post"]

        mallas = pd.read_excel(path, sheet, header=[0], dtype=str).fillna('')
        try:
            for _, row_chain in mallas.iterrows():
                chain = Chain(*row_chain[CHAIN_MAIN_KEYS])

                dependencies = split_rows(row_chain, CHAIN_DEPENDENCIES)
                for _, dependency in dependencies.iterrows():
                    if tuple(dependency) != ("", "", "", "", ""):
                        chain.add_dependency(ChainDependency(*tuple(dependency)))

                [chain.add_job(job) for job in self.get_jobs_chains(chain.chain)]

                self.chains.append(chain)
        except KeyError as e:
            raise ExcelKeyError(f"{sheet} has not the right column names for a chain sheet", sheet)

    def _read_jobs(self, path):
        sheet_names = pd.ExcelFile(path).sheet_names
        job_names = [_ for _ in filter(lambda x: "mallas" not in x, sheet_names)]
        for sheet in job_names:
            self._read_jobs_sheet(path, sheet)

    def _read_jobs_sheet(self, path, sheet):

        print(sheet)

        JOB_MAIN_KEYS = ["script", "jobname", "uuaa", "grupo_soporte", "maquina_origen", "libreria_origen",
                         "descripcion", "periodicidad", "sub_application", "host_ejecucion", "criticidad"]

        FICHEROBBDD = ["paso_ficherobbdd", "entrada_ficherobbdd", "salida_ficherobbdd", "entidades_ficherobbdd",
                       "tipo_acceso_ficherobbdd"]
        REARRANQUES = ["paso_rearranques", "predecesores_rearranques", "sucesores_rearranques", "normas_rearranques"]
        INCOMPATIBILIDADES = ["paso_incompatibilidad", "incompatibilidades_incompatibilidad",
                              "criticidad_incompatibilidad"]

        jobs = pd.read_excel(path, sheet, header=[0], dtype=str).fillna('')

        try:
            for _, row_job in jobs.iterrows():
                job = Job(*row_job[JOB_MAIN_KEYS])

                files = split_rows(row_job, FICHEROBBDD)
                for _, filebbdd in files.iterrows():
                    if tuple(filebbdd) != ("", "", "", "", ""):
                        job.add_filesanddb(FileAndDb(*tuple(filebbdd)))

                reruns = split_rows(row_job, REARRANQUES)
                for _, rerun in reruns.iterrows():
                    if tuple(rerun) != ("", "", "", ""):
                        job.add_norma_rearranque(RerunRule(*tuple(rerun)))

                incompatibilities = split_rows(row_job, INCOMPATIBILIDADES)
                for _, incompatibility in incompatibilities.iterrows():
                    if tuple(incompatibility) != ("", "", ""):
                        job.add_incompatibility(Incompatibility(*tuple(incompatibility)))

                self.jobs.append(job)
        except KeyError as e:
            raise ExcelKeyError(f"{sheet} has not the right column names for a chain sheet", sheet)

    def chain_names(self):
        return [chain.chain for chain in self.chains]

    def job_names(self, chains):
        return [_.jobname for _ in filter(lambda x: x.sub_application in chains, self.jobs)]

    def get_chains(self, chains):
        return [_ for _ in filter(lambda x: x.chain in chains, self.chains)]

    def get_jobs(self, jobs):
        return [_ for _ in filter(lambda x: x.chain in jobs, self.jobs)]

    def get_jobs_chains(self, chains):
        return [_ for _ in filter(lambda x: x.sub_application in chains, self.jobs)]

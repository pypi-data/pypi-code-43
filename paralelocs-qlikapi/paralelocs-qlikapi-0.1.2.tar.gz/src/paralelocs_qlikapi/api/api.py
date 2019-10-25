from paralelocs_qlikapi.api.auth import QlikAuth
from paralelocs_qlikapi.method import app, reloadtask, task, tag, stream
import requests



class QlikAPI():
    """

        Classe de High Level com a abstração de toda a complexidade da API.
        Todos os metodos serão disponibilizados nessa classe

    """

    def __init__(self,
                 hostname='localhost',
                 sslfile=None,
                 sslfile_key=None,
                 verify=True
                 ):

        self.auth = QlikAuth(
                                        hostname=hostname,
                                        sslfile=sslfile,
                                        sslfile_key=sslfile_key,
                                        verify=verify
                                            )
        self.session = requests.Session()
        self.app = app.App(auth = self.auth, session=self.session)
        self.reloadtask = reloadtask.Task(auth = self.auth, session=self.session)
        self.task = task.Task(auth = self.auth, session=self.session)
        self.tag = tag.Tag(auth = self.auth, session=self.session)
        self.stream = stream.Stream(auth = self.auth, session=self.session)
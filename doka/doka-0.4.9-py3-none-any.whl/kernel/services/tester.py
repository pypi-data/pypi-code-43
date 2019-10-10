from doka.kernel.definition.entities import UnitEntity
import json
import requests
from doka.kernel.services import docker
import uuid
from termcolor import colored


class Unit:
    def __init__(self, unit_entity: UnitEntity, silent_mode=False):
        self._unit_entity = unit_entity
        self._silent_mode = silent_mode

    def test_api(self):
        try:
            host = docker.Runtime().get_unit_ip(self._unit_entity)
        except:
            self._print(colored("Не могу получить IP сервиса. Возможно он не поднят", "red"))
            return
        for entry in self._unit_entity.codedir.joinpath(*['tests', 'api']).glob('**/*.json'):
            with entry.open('rt') as f:
                scenario = json.load(f)
                self._print("Сценарий:", colored("{}".format(scenario.get("title")), "yellow"))
                for case in scenario.get("cases", []):
                    self._print("\tКейс: ", colored(case.get("title"), "yellow"))
                    self._print("\t\tВыполняем операцию ", colored(case.get("operation"), "yellow"),
                                " с параметрами ",
                                colored(case.get("request"), "yellow"))
                    try:
                        response = requests.post('http://{}/api/jsonrpc'.format(host), json={
                            "jsonrpc": "2.0",
                            "method": case.get("operation"),
                            "id": str(uuid.uuid4()),
                            "params": case.get("request")
                        }).json()
                        self._print("\t\tПолучили ответ: ",
                                    colored(response.get("result") or response.get("error"), "yellow"))
                        self._print("\t\tДолжны были получить: ", colored(case.get("response"), "yellow"))
                        if response.get("result") != case.get("response"):
                            self._print(colored("\t\tОшибка!", "red"))
                        else:
                            self._print(colored("\t\tУспешно!", "green"))
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        self._print(colored("\t\tОшибка", "red"), " при отправке запроса: ", str(e))

    def _print(self, *args):
        if not self._silent_mode:
            print(*args)

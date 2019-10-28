import requests
import json
import time
import datetime

from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotAcceptable
from rest_framework import status

from integration_utils.mixins import CredentialMixin

from .models import Credential
from .base_views import BaseCredentialModelViewSet


class CredentialModelViewSet(BaseCredentialModelViewSet):

    def create(self, request, format=None):
        """must be implemented"""
        return Response({"status": "error", 'message': "IMPLEMENT ME"}, status=422)


class FilterAPIView(CredentialMixin, APIView):
    def get(self, request):
        """
        endpoint: /filter
        Must be IMPLEMENTED
        format Response:
        [
            {
                "code": "pipelines",
                "name": "Воронки продаж",
                "type": "MULTISELECT",
                "enums": [
                    {
                        "code": "default",
                        "value": "Продажи"
                    }
                ]
            },
            {
                "code": "managers",
                "name": "Менеджеры",
                "type": "MULTISELECT",
                "enums": [
                    {
                        "code": "1",
                        "value": "Заур Кокоев"
                    },
                    {
                        "code": "11",
                        "value": "Кирилл Баскаков"
                    },
                    {
                        "code": "13",
                        "value": "Иван Грибов"
                    },
                    {
                        "code": "15",
                        "value": "Павел Уваров"
                    },
                    {
                        "code": "17",
                        "value": "Сергей Луговской"
                    },
                    {
                        "code": "21",
                        "value": "Богдан Заводчиков"
                    },
                    {
                        "code": "29",
                        "value": "Игорь Кузин"
                    },
                    {
                        "code": "31",
                        "value": "Никита Карагин"
                    },
                    {
                        "code": "33",
                        "value": "Мирослава Кирсанова"
                    },
                    {
                        "code": "35",
                        "value": "Дмитрий Павлов"
                    },
                    {
                        "code": "37",
                        "value": "Леонид Пикуль"
                    },
                    {
                        "code": "39",
                        "value": "Василий Князев"
                    },
                    {
                        "code": "41",
                        "value": "Заур Кокоев"
                    }
                ]
            },
            {
                "code": "manager_groups",
                "name": "Группы менеджеров",
                "type": "MULTISELECT",
                "enums": [
                    {
                        "code": "1",
                        "value": "Группа 08"
                    },
                    {
                        "code": "7",
                        "value": "Orange Creative"
                    },
                    {
                        "code": "13",
                        "value": "Группа интеграций CRM"
                    },
                    {
                        "code": "11",
                        "value": "Колл-центр"
                    },
                    {
                        "code": "5",
                        "value": "Отдел продаж"
                    },
                    {
                        "code": "3",
                        "value": "Процессинг"
                    },
                    {
                        "code": "9",
                        "value": "Реклама"
                    },
                    {
                        "code": "23",
                        "value": "Группа Ивана Грибова"
                    },
                    {
                        "code": "19",
                        "value": "Группа Павла Уварова"
                    },
                    {
                        "code": "10",
                        "value": "Чат-боты"
                    }
                ]
            },
            {
                "code": "UF_CRM_1535708769",
                "name": "Горячий",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_1535708830",
                "name": "Ключевой клиент",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_1559659072082",
                "name": "Ссылка на проект",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_1560527083638",
                "name": "Предоплата",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_5C8B56FF4D241",
                "name": "Вероятность,%",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_5C8B56FF52817",
                "name": "Дата начала",
                "type": "TEXT",
                "enums": []
            },
        ]
        """
        print("WARNING: filter must be implemented")
        default_response = [
            {
                "code": "pipelines",
                "name": "Воронки продаж",
                "type": "MULTISELECT",
                "enums": [
                    {
                        "code": "default",
                        "value": "Продажи"
                    }
                ]
            },
            {
                "code": "managers",
                "name": "Менеджеры",
                "type": "MULTISELECT",
                "enums": [
                    {
                        "code": "1",
                        "value": "Заур Кокоев"
                    },
                    {
                        "code": "11",
                        "value": "Кирилл Баскаков"
                    },
                    {
                        "code": "13",
                        "value": "Иван Грибов"
                    },
                    {
                        "code": "15",
                        "value": "Павел Уваров"
                    },
                    {
                        "code": "17",
                        "value": "Сергей Луговской"
                    },
                    {
                        "code": "21",
                        "value": "Богдан Заводчиков"
                    },
                    {
                        "code": "29",
                        "value": "Игорь Кузин"
                    },
                    {
                        "code": "31",
                        "value": "Никита Карагин"
                    },
                    {
                        "code": "33",
                        "value": "Мирослава Кирсанова"
                    },
                    {
                        "code": "35",
                        "value": "Дмитрий Павлов"
                    },
                    {
                        "code": "37",
                        "value": "Леонид Пикуль"
                    },
                    {
                        "code": "39",
                        "value": "Василий Князев"
                    },
                    {
                        "code": "41",
                        "value": "Заур Кокоев"
                    }
                ]
            },
            {
                "code": "manager_groups",
                "name": "Группы менеджеров",
                "type": "MULTISELECT",
                "enums": [
                    {
                        "code": "1",
                        "value": "Группа 08"
                    },
                    {
                        "code": "7",
                        "value": "Orange Creative"
                    },
                    {
                        "code": "13",
                        "value": "Группа интеграций CRM"
                    },
                    {
                        "code": "11",
                        "value": "Колл-центр"
                    },
                    {
                        "code": "5",
                        "value": "Отдел продаж"
                    },
                    {
                        "code": "3",
                        "value": "Процессинг"
                    },
                    {
                        "code": "9",
                        "value": "Реклама"
                    },
                    {
                        "code": "23",
                        "value": "Группа Ивана Грибова"
                    },
                    {
                        "code": "19",
                        "value": "Группа Павла Уварова"
                    },
                    {
                        "code": "10",
                        "value": "Чат-боты"
                    }
                ]
            },
            {
                "code": "UF_CRM_1535708769",
                "name": "Горячий",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_1535708830",
                "name": "Ключевой клиент",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_1559659072082",
                "name": "Ссылка на проект",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_1560527083638",
                "name": "Предоплата",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_5C8B56FF4D241",
                "name": "Вероятность,%",
                "type": "TEXT",
                "enums": []
            },
            {
                "code": "UF_CRM_5C8B56FF52817",
                "name": "Дата начала",
                "type": "TEXT",
                "enums": []
            },
        ]
        return Response(default_response)


class SelectionAPIView(CredentialMixin, APIView):
    def get(self, request):
        """
        endpoint: /selection
        Must be IMPLEMENTED
        format Response:
        [
            {
                "code": 1,
                "name": "TEST",
                "enums": [],
                "TYPE": "TEXT"
            }
        ]
        """
        print("WARNING: selection must be implemented")
        return Response([
            {
                "code": 1,
                "name": "TEST",
                "enums": [],
                "TYPE": "TEXT"
            }
        ])


class CalculationAPIView(CredentialMixin, APIView):
    def get(self, request, format=None):
        """
        endpoint: /calculation
        This default endpoint
        """
        _ = self.get_credential(request, Credential)
        data = [{"code": "first_cost", "name": "Себестоймость", "type": "NUMERIC"},
                {"code": "transaction_amount", "name": "Расход", "type": "NUMERIC"}]
        return Response(data)

import enum
from typing import List
from dataclasses import dataclass

import requests


class OptionEnum(enum.Enum):
    def __str__(self):
        return str(self.value)


class QuestionOriginal(OptionEnum):
    YES = 1
    NO = 0
    ALL = 2


class QuestionGeneration(OptionEnum):
    ALL = "all"
    REFORM = 1
    MSM1 = 2
    MSM2 = 3


class QuestionRating(OptionEnum):
    ALL = 3
    UNRATED = 2
    GOOD = 1
    BAD = 0


class OlmenSession:
    def __init__(self):
        self.session = requests.Session()

    def login(self, user: str, password: str):
        data = {"username": user, "password": password}
        response = self.session.post(
            "http://api.olmen.de/api/login", json=data
        )
        self.session.headers.update({
            "X-Access-Token": f"Bearer {response.json()['token']}",
        })
        return self

    def get(self, url, data=None):
        response = self.session.get(url, json=data)
        response.raise_for_status()
        response_data = response.json()
        return response_data


@dataclass
class Module:
    id: str
    name: str
    code: str
    category: str


def create_module(data: dict) -> Module:
    return Module(
        id=data["id"],
        name=data["name"],
        code=data["code"],
        category=data["category"]
    )


@dataclass
class Question:
    id: str
    question_text: str
    answer_options: List[str]
    solution_index: int
    rating: int = 0
    original: QuestionOriginal = QuestionOriginal.ALL
    generation: QuestionGeneration = QuestionGeneration.ALL
    discussion: str = ""


def create_question(data: dict) -> Question:
    return Question(
        id=data["id"],
        question_text=data["question"].strip(),
        answer_options=data["answers"],
        rating=int(data["rating"]),
        original=QuestionOriginal(int(data["original"])),
        generation=QuestionGeneration(int(data["generation"])),
        discussion=data["discussion"],
        solution_index=data["solution"],
    )



class Olmen:
    def __init__(self, session):
        self.session = session
        self.modules = None

    def get_modules(self):
        self.modules = [create_module(m) for m in self.session.get("http://api.olmen.de/api/modules")]

    def get_module(
            self,
            module_id: str,
            rating: QuestionRating = QuestionRating.ALL,
            generation: QuestionGeneration = QuestionGeneration.ALL,
            original: QuestionOriginal.ALL = QuestionOriginal.ALL,
    ):
        questions = self.session.get(
            f"http://api.olmen.de/api/mcqs/modules/{module_id}/rating/{rating}/generation/{generation}/original/{original}/number/0")
        return [create_question(q) for q in questions]

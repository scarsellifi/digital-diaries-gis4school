import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import re
from security import encrypt, decrypt
from credentials import KEY
from db import engine
from sqlalchemy import text
from models.question import Question
import json

import pprint

pp = pprint.PrettyPrinter(indent=4)


class Survey:
    def __init__(self):
        self.info = {}

    def get_id_information(self, url):
        url = decrypt(url, KEY)
        url_option = url.split("&")
        id = url_option[0]
        survey_id = url_option[1]
        batteries_id = json.loads(url_option[2])
        title = url_option[3]

        regex = re.findall(r"\d+", id)
        self.info = {
            "id": id,
            "group_id": regex[0],
            "member_number": regex[1],
            "survey_id": survey_id,
            "batteries_id": batteries_id,
            "title": title,
        }

        return self.info

    @staticmethod
    def create_survey_url(
        id: str, survey_id: str, batteries_id: list, title: str, key
    ) -> str:
        string = id + "&" + survey_id + "&" + str(batteries_id) + "&" + title
        url = encrypt(string, KEY)
        URL = "https://euronike.eu.pythonanywhere.com/survey/"
        return URL + url


class StoreAnswerData:
    def __init__(self, data):
        self.data = data
        self.code_id = self.data["code_id"]
        self.group_id = self.data["group_id"]
        self.survey_id = self.data["survey_id"]

    def get_answers_collection(self):
        self.answers_collection = []
        self.answers = self.data
        del self.answers["code_id"]
        del self.answers["group_id"]
        del self.answers["survey_id"]
        for question_id in self.answers:
            question_info = Question.get_question_info(question_id)
            single_answer = {
                "code_id": self.code_id,
                "survey_id": self.survey_id,
                "group_id": self.group_id,
                "question_id": question_id,
                "q_type": question_info["q_type"],
                "q_number": question_info["q_number"],
                "q_value": self.answers[question_id],
            }
            self.answers_collection.append(single_answer)

        return self.answers_collection

    def save_data_to_db(self):
        answers_data = self.answers_collection

        with engine.connect() as con:
            statement = text(
                """INSERT into responses
                                (code_id, survey_id, group_id,  question_id, q_type, q_number, q_value)
                                values (:code_id, :survey_id, :group_id,  :question_id, :q_type, :q_number, :q_value); """
            )
            con.execute(statement, answers_data)
            # for line in data:
            #    con.execute(statement, **line)

        return self

    def save(self):
        self.get_answers_collection()
        self.save_data_to_db()

"""
admin model
"""

import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from db import engine  # pylint: disable=wrong-import-position
from telegram import PyBot  # pylint: disable=wrong-import-position
from credentials import TOKEN, KEY  # pylint: disable=wrong-import-position
from models.survey import Survey  # pylint: disable=wrong-import-position
from log import log_obj  # pylint: disable=wrong-import-position


class upload_db_question:
    """upload db question"""

    def __init__(self, df):
        self.df = df

    def upload(self):
        data = self.df.to_dict(orient="records")

        with engine.connect() as con:
            statement = text(
                """INSERT
                	        INTO questions
                            (id,	group_type,	group_id,	"TIMING",	"TIMING_NAME",	battery_id,	intro,	q_type,	question,	category,	min,	mid,	max,	list_values,	s_index )
                            values(:id,	:group_type,	:group_id,	:TIMING,	:TIMING_NAME,	:battery_id,	:intro,	:q_type,	:question,	:category,	:min,	:mid,	:max,	:list_values,  :s_index) """
            )
            for row_data in data:
                result = con.execute(statement, row_data)

        return result


class upload_db_calendar:
    """upload db calendar"""

    def __init__(self, df):
        self.df = df

    def upload(self):
        data = self.df.to_dict(orient="records")

        with engine.connect() as con:
            statement = text(
                """INSERT
                    INTO calendar
                    (survey_id,	datetime,	battery_ids,	"TIMING",	group_id, title )
                    values(:survey_id,	:datetime,	:battery_ids,	:TIMING,	:group_id, :title) """
            )
            for row_data in data:
                result = con.execute(statement, row_data)

        return result


class manage_survey:
    """manage survey"""

    def __init__(self):
        self.survey_data: dict
        self.users_data: list
        self.group_data: list

    def get_survey_data(self) -> dict:
        """get data survey from calendar"""
        with engine.connect() as con:
            self.survey_data = {}
            statement = text("""select * from calendar""")
            result = con.execute(statement)
            for row in result:
                self.survey_data[str(dict(row)["survey_id"])] = dict(row)
        return self.survey_data

    def get_users_data(self):
        """get telegram user id and group"""
        with engine.connect() as con:
            self.users_data = []
            statement = text("""select * from telegram_user""")
            result = con.execute(statement)
            for row in result:
                self.users_data.append(dict(row))
        return self.users_data

    def get_group_data(self, group_id: str):
        """get data and filter by group"""
        self.get_users_data()
        self.group_data: list = []
        for item in self.users_data:
            if item["code_id"][0] == group_id:
                self.group_data.append(item)
        return self.group_data

    def get_group_telegram_ids(self, group_id: str):
        """get group telegram ids"""
        telegram_ids: list = []
        group_data = self.get_group_data(group_id)
        for item in group_data:
            telegram_ids.append(item["id"])

        return telegram_ids

    def send_survey_to_group(self, survey_id: str, message: str):
        survey_data = self.get_survey_data()
        specific_survey = survey_data[survey_id]
        bot = PyBot(TOKEN)
        user_data_collection = self.get_group_data(
            specific_survey["group_id"]
        )  # this must be correct for pupils

        for user_data in user_data_collection:
            url = Survey.create_survey_url(
                user_data["code_id"],
                str(specific_survey["survey_id"]),
                specific_survey["battery_ids"],
                specific_survey["title"],
                KEY,
            )
            send_message = f"{message}: {url}"
            # bot.sendMessage(user_data['id'], "Please answer the questionnaire by tonight")
            bot.sendMessage(user_data["id"], send_message)
            log_obj("send_survey_to_group").write(
                {
                    "code_id": user_data["code_id"],
                    "survey_id": str(specific_survey["survey_id"]),
                    "battery_ids": specific_survey["battery_ids"],
                    "title": specific_survey["title"],
                }
            )

    def send_survey_to_admin(self, survey_id: str, message: str):
        survey_data = self.get_survey_data()
        specific_survey = survey_data[survey_id]
        bot = PyBot(TOKEN)
        user_data_collection = self.get_group_data("0")

        for user_data in user_data_collection:
            url = Survey.create_survey_url(
                user_data["code_id"],
                str(specific_survey["survey_id"]),
                specific_survey["battery_ids"],
                specific_survey["title"],
                KEY,
            )
            send_message = f"{message}: {url}"
            bot.sendMessage(user_data["id"], send_message)


if __name__ == "__main__":
    import pandas as pd

    data = pd.read_excel("db_questions.xlsx", sheet_name=None, keep_default_na=False)
    # print(data)
    questions = data["questions"]

    try:
        Upload_question = upload_db_question(questions)
        print(Upload_question.upload())
    except Exception as e:
        print(e)

    try:
        calendar = data["calendar"][
            ["survey_id", "datetime", "battery_ids", "TIMING", "group_id", "title"]
        ]
        calendar["datetime"] = calendar["datetime"].astype(str)
        Upload_question = upload_db_calendar(calendar)
        print(Upload_question.upload())
    except Exception as e:
        print(e)

    Manage = manage_survey()

    print(Manage.get_users_data())
    print(Manage.get_group_data("0"))

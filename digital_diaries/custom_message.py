"""
send custom message to specific groups
"""

from pybot import PyBot
from credentials import TOKEN
from models.admin import manage_survey


class CustomMessage:
    def __init__(self, flask_request_form_to_dict: dict):
        self.data = flask_request_form_to_dict
        self._get_group_list = None
        self._message = None

    def get_group_list(self):
        data = self.data.copy()
        del data["message"]
        self._get_group_list = [x.split("_")[0] for x in data.keys()]
        return self._get_group_list

    def get_message(self):
        data = self.data.copy()
        self._message = data["message"]
        return self._message

    def send_message_to_groups(self):
        connection = manage_survey()
        user_data = connection.get_users_data()
        user_dict = {x["id"]: x["code_id"] for x in user_data}
        pybot = PyBot(TOKEN)
        for group in self._get_group_list:

            telegram_ids = connection.get_group_telegram_ids(group_id=str(group))
            for telegram_id in telegram_ids:

                code_id = user_dict[telegram_id]
                local_message = self._message.replace("code_id", code_id)
                local_message = local_message.replace("usp=pp_url&", "")

                pybot.sendMessage(telegram_id, local_message)
                print(telegram_id, code_id)
        return self

import requests
from credentials import TOKEN, TEST_USER_TELEGRAM
from log import log_obj


class PyBot:
    def __init__(self, TOKEN):
        self.TOKEN = TOKEN

    def sendMessage(self, user, message):
        requests.get(
            f"https://api.telegram.org/bot{self.TOKEN}/sendMessage?chat_id={user}&text={message}"
        )
        log_obj("sendMessage").write({"user": user, "message": message})

    def sendMessageToUserList(self, user_list, message):
        for user in user_list:
            self.sendMessage(user, message)

"""
this module handle message from telegram
"""
from cryptography.fernet import Fernet
from hashids import Hashids
from models.user import User
from credentials import TOKEN, KEY
from pybot import PyBot
import config

hashids = Hashids(TOKEN)

def encrypt(message: str, key: bytes) -> str:
    message = str.encode(message)
    return Fernet(key).encrypt(message).decode()

def decrypt(token: str, key: bytes) -> str:
    token = str.encode(token)
    token = Fernet(key).decrypt(token)
    return token.decode()

class message_handler:
    @staticmethod
    def build_response(update):
        pybot = PyBot(TOKEN)
        if "message" in update:
            message = update["message"]
            telegram_id = message["from"]["id"]
            current_user = User()
            status = current_user.telegram_user_logged(telegram_id)
            #STATUS === True - LOGGED
            if (
                status
                and message["text"] != "/feedback"
                and message["text"] != "/test_euronike"
            ):
                pybot.sendMessage(
                    telegram_id,
                    f"Hi, your survey code is: {current_user.code_id} and you are correctly logged",
                )
                pybot.sendMessage(
                    telegram_id,
                    f"You can find some information about the project at {config.URL}",
                )
                pybot.sendMessage(
                    telegram_id,
                    f"wait for your survey link ... or give us feedback with /feedback command",
                )
                # inserire logica dei questionari (uno subito e poi gli altri in base a range temporali o invii diretti)
            elif status and message["text"] == "/feedback":
                pybot.sendMessage(
                    telegram_id,
                    f'send us feedback at this link: {config.URL}/survey/{encrypt(current_user.code_id + "&" + "feedback" + "&" + "[9]" + "&" + "TITOLO FEEDBACK", KEY)}',
                )
            elif status and message["text"] == "/test_euronike":
                pybot.sendMessage(
                    telegram_id,
                    f'send us feedback at this link: {config.URL}/survey/{encrypt(current_user.code_id + "&" + "test" + "&" + "[1,2,3,4,5,6,7,8,9]" + "&" + "TITOLO TEST", KEY)}',
                )
            #STATUS === false not logged!
            elif message["text"] == "/start":
                pybot.sendMessage(
                    telegram_id,
                    "hi, "
                    + "Enter the code that was given to you at school (or write /help )",
                )
            #STATUS === false not logged 
            elif message["text"] == "/help":
                pybot.sendMessage(
                    telegram_id,
                    f"You can find some information about the project at {config.URL} ",
                )
            #STATUS === telegram logging with code_list and telegram_user 
            else:
                if current_user.code_check(message["text"]):
                    current_user.telegram_association(telegram_id, message["text"])
                    pybot.sendMessage(telegram_id, "you are logged correctly")
                    pybot.sendMessage(
                        telegram_id,
                        f"You can find some information about the project at {config.URL} ",
                    )
                    pybot.sendMessage(
                        telegram_id,
                        f"wait for your survey link ... or give us feedback with /feedback command",
                    )
            # 
                else:
                    pybot.sendMessage(
                        telegram_id,
                        "Please, "
                        + "insert a correct code to proceed (or write /help for more info)",
                    )
        # telegram logging with code_list and telegram_user fail: wrong code_list id
        else:
            pass


if __name__ == "__main__":
    print(encrypt("feedback", KEY))

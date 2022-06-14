"""
THIS MODULE CREATE code_list TABLE
code_list is useful to decouple / anonimize telegram user to students without lose data trends
ATTENTION: SAVE TO DB ONLY ONE TIME!!
"""

import os
import sys
import random
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from db import engine  # pylint: disable=wrong-import-position


class Registration:
    """
    CREATE code_list with anonymus code and save to db
    """

    def __init__(self):
        pass

    @staticmethod
    def randomWord(length=7, base=""):
        consonants = "bcdfghjklmnpqrstvwxyz"
        vowels = "aeiou"

        word = "".join(
            random.choice((consonants, vowels)[i % 2]) for i in range(length)
        )
        complete = base + word
        return complete

    @staticmethod
    def create_code_list(group_n=10, user_n=80):
        data = []
        for group in range(0, group_n + 1):
            for user in range(0, user_n + 1):
                data.append(
                    {
                        "entity_n": group,
                        "user_n": user,
                        "code": f"{group}{Registration.randomWord(7)}{user}",
                    }
                )
        return data

    @staticmethod
    def save_code_list_to_db(data):
        with engine.connect() as con:
            statement = text(
                """INSERT INTO code_list (entity_n, user_n, code) VALUES (:entity_n, :user_n, :code) """
            )
            result = con.execute(statement, data)
        return result

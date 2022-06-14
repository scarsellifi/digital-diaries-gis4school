import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from db import engine
from sqlalchemy import text


class User:
    def __init__(self):
        self.code_id = None
        self.status = None  # teacher student, admin, not_registered

    def code_check(self, code_id):
        data = {"code_id": code_id}
        result_list = []

        with engine.connect() as con:
            statement = text("""SELECT * FROM code_list where code = :code_id""")
            result = con.execute(statement, data)

        for row in result:
            result_list.append(row)

        self.user_data = {"data": result_list, "columns_name": result.keys()}

        if len(self.user_data["data"]) == 1:
            return True
        else:
            return False

    def telegram_association(self, telegram_id, code_id):
        data = {"code_id": code_id, "telegram_id": telegram_id}

        with engine.connect() as con:
            statement = text(
                """INSERT INTO telegram_user (id, code_id )  values(:telegram_id, :code_id) """
            )
            result = con.execute(statement, data)

        return result

    def telegram_user_logged(self, telegram_id):
        data = {"telegram_id": telegram_id}
        result_list = []

        with engine.connect() as con:
            statement = text("""SELECT * FROM telegram_user where id = :telegram_id""")
            result = con.execute(statement, data)

        for row in result:
            result_list.append(row)

        self.login = {"data": result_list, "columns_name": result.keys()}
        print(self.login)

        if len(self.login["data"]) == 1:
            self.code_id = self.login["data"][0][1]
            print(self.code_id)
            return True
        else:
            return False

    def telegram_login(self):
        # check if already exist a link from code_id to telegram i
        pass


if __name__ == "__main__":
    from credentials import TEST_USER_TELEGRAM

    new_user = User()
    new_user.telegram_user_logged(str(TEST_USER_TELEGRAM))

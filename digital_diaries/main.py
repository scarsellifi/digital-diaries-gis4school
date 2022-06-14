"""
main module - start flask instance
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from telegram import message_handler
import credentials
from models.survey import Survey, StoreAnswerData
from models.question import render_survey
from models.admin import manage_survey
from custom_message import CustomMessage

os.environ["TZ"] = "Europe/Rome"
# try:
#     time.tzset()
# except Exception as e:
#     print

print("activate")

app = Flask(__name__)
app.config["SECRET_KEY"] = credentials.SECRET

cors = CORS(app, resources={r"*": {"origins": "*"}})
requests.get(
    f"https://api.telegram.org/bot{credentials.TOKEN}/setWebhook?url={credentials.URL}"
)


@app.route("/")
def main():
    """
    render homepage
    """
    return render_template("index.html")


@app.route("/survey/<url>")
def survey(url):
    """
    render custom page for survey.
    """
    survey_info = Survey().get_id_information(url)
    batteries_id = survey_info["batteries_id"]
    return render_template(
        "survey_template_testing.html",
        survey_info=survey_info,
        batteries=render_survey(batteries_id).to_html(),
    )


@app.route("/survey/<url>/test")
def survey_test(url):
    """
    render custom page for survey: for testing only
    """
    survey_info = Survey().get_id_information(url)
    batteries_id = survey_info["batteries_id"]
    return render_template(
        "survey_template_testing.html",
        survey_info=survey_info,
        batteries=render_survey(batteries_id).to_html(),
    )


@app.route("/survey/post", methods=["POST"])
def post():
    """
    this route save data from single survey responses
    """
    payload = request.form.to_dict()
    data = StoreAnswerData(payload)
    data.save()
    jsonify(request.form)
    return render_template("thankyou.html")


@app.route(f"/{credentials.SECRET}", methods=["POST"])
def webhook():
    """
    this route interact with telegram
    """
    update = request.get_json()
    message_handler.build_response(update)

    return "OK"


@app.route("/admin/555666555/<survey_id>", methods=["GET"])
def send_survey(survey_id):
    """
    this route send specific survey to groups in calendar
    """
    survey_id = str(survey_id)
    try:
        manage = manage_survey()
        manage.send_survey_to_group(
            survey_id=survey_id,
            message=f"Fill in the following questionnaire [id {survey_id}]",
        )
        manage.send_survey_to_admin(
            survey_id=survey_id,
            message=f"Fill in the following questionnaire [id {survey_id}] - admin check",
        )
        return "ok"

    except Exception as err:
        return str(err)


@app.route("/send_custom_message", methods=["GET", "POST"])
def send_custom_message():
    """gui for sending custom message to group"""
    if request.method == "GET":
        return render_template("send_custom_message.html")
    else:
        message = dict(request.form)
        if message["password"] == credentials.SECRET:
            cmsg = CustomMessage(message)
            print(cmsg.get_group_list())
            print(cmsg.get_message())
            print(cmsg.send_message_to_groups())
            return str(dict(request.form))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

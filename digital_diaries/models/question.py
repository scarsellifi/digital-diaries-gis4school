import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from db import engine
from sqlalchemy import text
import json


class Question:
    def __init__(self, q_type, q_number, question_text):
        self.question_id = f"{q_type}{q_number}"
        self.q_type = q_type
        self.q_number = q_number
        self.question_text = question_text

    @staticmethod
    def get_question_info(question_id):
        info_list = question_id.split("_")
        question_info = {"q_type": info_list[0], "q_number": info_list[1]}

        return question_info


class Slider(Question):
    def render_question(self):
        template = f"""
            <div>
                <label> question 1 </label>
                <input name= "slider_1" class="slider" id="slider_0" type="text" value="" class="irs-hidden-input" tabindex="-1" readonly="">
            </div>
        """


class Select(Question):
    def set_modalities(self, modalities_list):
        self.modalities_list = modalities_list

    # render question


class Textarea(Question):
    def set_max_len(self, max_len=3000):
        self.max_len = max_len


class render_battery:
    def __init__(self, battery_id):
        self.battery_id = battery_id

    def get_data(self):

        data = {"battery_id": str(self.battery_id)}

        self.list_result = []

        with engine.connect() as con:
            statement = text(
                """SELECT *
                            FROM questions
                            WHERE battery_id = :battery_id
                            """
            )
            battery_table = con.execute(statement, data)

        for row in battery_table:
            self.list_result.append(dict(row))

        return self.list_result

    def get_intro(self):
        self.intro = self.list_result[0]["intro"]
        return self.intro

    def get_list_values(self):
        self.list_values = self.list_result[0]["list_values"]
        self.list_values = json.loads(self.list_values)
        return self.list_values

    def get_q_type(self):
        self.q_type = self.list_result[0]["q_type"]
        return self.q_type

    def render_question(self, q_type):
        pass

    def render_slide_questions(self):
        self.html = ""
        for item in self.list_result:

            question = item["question"]
            question_id = item["s_index"]
            question_q_type = item["q_type"]

            question_min = self.list_values[0]
            question_mid = self.list_values[1]
            question_max = self.list_values[2]
            question_min_description = item["min"]
            question_mid_description = item["mid"]
            question_max_description = item["max"]

            template = f"""
            <div>
                <label> {question} </label>

                <input name= "{question_q_type}_{question_id}" class="slider" id="{question_id}" type="text" value="" class="irs-hidden-input" tabindex="-1" readonly="">
                <p> <small class="text-muted"> point value: </small>
                <small class="text-muted"><b>{question_min}</b> - {question_min_description}.</small>
                <small class="text-muted"><b>{question_mid}</b> - {question_mid_description}.</small>
                <small class="text-muted"><b>{question_max}</b> - {question_max_description}.</small>
                </p>
            </div>
            """
            self.html += template
        return self.html

    def render_slide_battery_with_js(self):

        title = self.intro

        template = f"""<div class="card">
                    <div class="card-body">
                        <h5 class="card-title"> {title} </h5>
                        <div class="slider__body">
                            {self.html}
                        </div>
                    </div>
                </div>

        """
        question_min = self.list_values[0]
        question_mid = self.list_values[1]
        question_max = self.list_values[2]

        script = f"""
                <script>
                var result = null;
                $(".slider").ionRangeSlider({{
                    min: {question_min},
                    max: {question_max},
                    from: {question_mid},
                    skin: "big",
                    onStart: function (data) {{
                        // fired then range slider is ready
                    }},
                    onChange: function (data) {{
                        // fired on every range slider update
                    }},
                    onFinish: function (data) {{
                        // fired on pointer release
                        result = data;
                        console.log(result.from)
                        // BUT YOU MUST TAKE VALUE FROM ID at the moment of the post!
                    }},
                    onUpdate: function (data) {{
                        // fired on changing slider with Update method
                    }}
                }});
                </script>
                """

        self.slide_battery_with_js_html = template + script
        return self.slide_battery_with_js_html

    def render_select_questions(self):
        self.html = ""
        for item in self.list_result:

            question = item["question"]
            question_id = item["s_index"]
            question_q_type = item["q_type"]
            question_category = item["category"]
            # question_category.replace("“", "'")
            question_options = json.loads(question_category)

            self.option_list_rendered: str = ""
            for value, text in question_options.items():
                self.option_list_rendered += f"<option value={value}>{text}</option>"

            template = f"""<h5 class="card-title">{question}</h5>
                        <select name="{question_q_type}_{question_id}" class="form-select" aria-label="Default select example">
                        {self.option_list_rendered}
                        </select> """

            self.select_question_html = template
        return self.select_question_html

    def render_select_battery(self):

        self.select_battery_html = f"""<div class="card">
                        <div class="card-body">
                        {self.select_question_html}
                        </div>
                    </div>"""
        return self.select_battery_html

    def render_radio_questions(self):
        self.html = ""
        for item in self.list_result:

            question = item["question"]
            question_id = item["s_index"]
            question_q_type = item["q_type"]
            question_category = item["category"]
            # question_category.replace("“", "'")
            radio_options = json.loads(question_category)

            self.radio_list_rendered: str = (
                f"""<h5 class="card-title">{question}</h5>"""
            )

            for value, text in radio_options.items():
                self.radio_list_rendered += f""" <div class="form-check">
                        <input class="form-check-input" type="radio" name="{question_q_type}_{question_id}" id="{question_q_type}_{question_id}_{value}" value="{value}">
                        <label class="form-check-label" for="{question_q_type}_{question_id}_{value}">
                            {text}
                        </label>
                    </div>"""

            template = self.radio_list_rendered

            self.radio_question_html = template
        return self.radio_question_html

    def render_radio_battery(self):
        self.radio_battery_html = f"""<div class="card">
                        <div class="card-body">
                        {self.radio_question_html}
                        </div>
                    </div>"""
        return self.radio_battery_html

    def render_textarea_questions(self):
        self.html = ""
        for item in self.list_result:

            question = item["question"]
            question_id = item["s_index"]
            question_q_type = item["q_type"]

            template = f"""<h5 class="card-title">{question}</h5>
                        <div>
                            <label for="{question_q_type}_{question_id}" class="form-label"></label>
                            <textarea name="{question_q_type}_{question_id}" class="form-control" id="{question_q_type}_{question_id}" rows="3"></textarea>
                        </div> """

            self.textarea_question_html = template
        return self.textarea_question_html

    def render_textarea_battery(self):

        self.textarea_battery_html = f"""<div class="card">
                        <div class="card-body">
                        {self.textarea_question_html}
                        </div>
                    </div>"""
        return self.textarea_battery_html

    def execute_slider(self):
        self.get_data()
        self.get_intro()
        self.get_list_values()
        self.get_q_type()
        self.render_slide_questions()
        return self.render_slide_battery_with_js()

    def execute_select(self):
        self.get_data()
        self.get_intro()
        self.get_q_type()
        self.render_select_questions()
        return self.render_select_battery()

    def execute_radio(self):
        self.get_data()
        self.get_intro()
        self.get_q_type()
        self.render_radio_questions()
        return self.render_radio_battery()

    def execute_textarea(self):
        self.get_data()
        self.get_intro()
        self.get_q_type()
        self.render_textarea_questions()
        return self.render_textarea_battery()

    def execute(self):
        self.get_data()
        self.get_q_type()
        if self.q_type == "slider":
            return self.execute_slider()
        elif self.q_type == "select":
            return self.execute_select()
        elif self.q_type == "textarea":
            return self.execute_textarea()
        elif self.q_type == "radio":
            return self.execute_radio()


class render_survey:
    def __init__(self, battery_ids: list) -> str:
        self.battery_ids = battery_ids

    def to_html(self):
        self.html: str = ""
        for battery_id in self.battery_ids:
            Render_battery = render_battery(battery_id)
            self.html += Render_battery.execute()

        return self.html

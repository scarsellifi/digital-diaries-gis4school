"""
db setting
"""
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
)
from sqlalchemy.sql import func


from credentials import DB_FILE

engine = create_engine(DB_FILE)
if __name__ == "__main__":

    meta = MetaData()

    """ Base = automap_base()
    Base.prepare(engine, reflect=True)
    code_list = Base.classes.code_list
    """
    code_list = Table(
        "code_list",
        meta,
        Column("code", String(30), primary_key=True, unique=True),
        Column("user_n", String(4)),
        Column("entity_n", String(3)),
    )

    telegram_user = Table(
        "telegram_user",
        meta,
        Column("id", String(20), primary_key=True, unique=True),
        Column("code_id", String(30), ForeignKey("code_list.code"), nullable=False),
    )

    survey = Table(
        "responses",
        meta,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", DateTime(timezone=True), server_default=func.now()),
        Column("code_id", String(30), ForeignKey("code_list.code"), nullable=False),
        Column("survey_id", String(30), nullable=False),
        Column("group_id", String(30), nullable=False),
        Column("question_id", String(30), nullable=False),
        Column("q_type", String(30), nullable=False),
        Column("q_number", String(30), nullable=False),
        Column("q_value", Text),
    )

    question = Table(
        "questions",
        meta,
        Column("id", Integer, primary_key=True),
        Column("group_type", String(30), nullable=False),
        Column("group_id", String(30), nullable=False),
        Column("TIMING", String(30), nullable=False),
        Column("TIMING_NAME", Text, nullable=False),
        Column("battery_id", String(30), nullable=False),
        Column("intro", Text, nullable=False),
        Column("q_type", String(30), nullable=False),
        Column("question", Text, nullable=False),
        Column("category", Text),
        Column("min", Text),
        Column("mid", Text),
        Column("max", Text),
        Column("list_values", Text),
        Column("s_index", Integer, unique=True),
    )

    calendar = Table(
        "calendar",
        meta,
        Column("survey_id", Integer, primary_key=True),
        Column("datetime", DateTime(timezone=True)),
        Column("battery_ids", Text, nullable=False),
        Column("TIMING", String(30), nullable=False),
        Column("group_id", String(30), nullable=False),
        Column("title", Text, nullable=False),
    )

    meta.create_all(engine)

from flask_sqlalchemy import SQLAlchemy

from base import Base

db = SQLAlchemy(
    model_class=Base,
    engine_options={
        "pool_pre_ping": True,
    },
)

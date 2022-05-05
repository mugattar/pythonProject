from pony.orm import Database, Required, Json
from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """
    The state of the user inside the scenario.
    """
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    """
    Application for registration.
    """
    name = Required(str)
    email = Required(str)
    university = Required(str)
    report = Required(str)
    section = Required(str)
    scientific_supervisor = Required(str)


db.generate_mapping(create_tables=True)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship is visited by many scientists through missions
    missions = db.relationship(
        "Mission", backref="planet", cascade="all, delete-orphan")

    # Add serialization rules (-missions.planet,)
    serialize_rules = ("-missions.planet",)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship (visits many planets through missions)
    missions = db.relationship(
        "Mission", backref="scientist", cascade="all, delete-orphan")

    # Add serialization rules (-missions.scientist,)
    serialize_rules = ("-missions.scientist",)

    # Add validation for name, field of study
    @validates('name')
    def validate_name(self, key, name):
        if name and len(name) >= 1:
            return name
        else:
            raise ValueError("Must have valid name attribute")

    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if field_of_study and len(field_of_study) >= 1:
            return field_of_study
        else:
            raise ValueError("Must have valid field of study attribute")


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationships (foreign keys for planet and scientist)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"))
    scientist_id = db.Column(db.Integer, db.ForeignKey("scientists.id"))

    # Add serialization rules (planet.missions, scientist.missions)
    serialize_rules = ("-planet.missions", "-scientist.missions")

    # Add validation (needs name, planet_id, scientist_id)
    @validates('name')
    def validate_name(self, key, name):
        if name and len(name) >= 1:
            return name
        else:
            raise ValueError("Must have valid name attribute")

    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if planet_id:
            return planet_id
        else:
            raise ValueError("Must have valid planet id attribute")

    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if scientist_id:
            return scientist_id
        else:
            raise ValueError("Must have valid scientist id attribute")

# add any models you may need.

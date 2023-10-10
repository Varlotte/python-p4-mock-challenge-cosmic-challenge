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

    def __init__(self, name, distance_from_earth, nearest_star):
        self.name = name
        self.distance_from_earth = distance_from_earth
        self.nearest_star = nearest_star

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship(
        "Mission", backref="planet", lazy=True, cascade="all, delete-orphan")
    # is visited by many scientists through missions
    # cascade deleletes
    # Add serialization rules
    serialize_rules = ("-missions.planet", )


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    def __init__(self, name, field_of_study):
        self.name = name
        self.field_of_study = field_of_study

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship
    missions = db.relationship(
        "Mission", backref="scientist", lazy=True, cascade="all, delete-orphan")
    # visits many planets through missions
    # cascade deletes
    # Add serialization rules
    serialize_rules = ("-missions.scientist",)

    # Add validation for name and field of study

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("Must have a name")
        return value

    @validates('field_of_study')
    def validate_field_of_study(self, key, value):
        if not value:
            raise ValueError("Must have a field of study")
        return value


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    def __init__(self, name, scientist_id, planet_id):
        self.name = name
        self.scientist_id = scientist_id
        self.planet_id = planet_id

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationships
    # belongs to both scientist and planet
    planet_id = db.Column(db.Integer, db.ForeignKey(
        'planets.id'), nullable=False)

    scientist_id = db.Column(db.Integer, db.ForeignKey(
        'scientists.id'), nullable=False)
    # Add serialization rules
    serialize_rules = ("-planet.missions", "-scientists.missions",)

    # Add validation name, scientist_id, planet_id

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("Must have a name")
        return value

    @validates('scientist_id')
    def validate_scientist_id(self, key, value):
        if not value:
            raise ValueError("Must have a valid scientist id")
        return value

    @validates('planet_id')
    def validate_planet_id(self, key, value):
        if not value:
            raise ValueError("Must have a valid planet id")
        return value


# add any models you may need.

#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

# initialize restful api
api = Api(app)

# @app.route('/')
# def home():
#     return ''

# get all planets from API


class PlanetList(Resource):
    def get(self):
        planets = Planet.query.all()
        return [planet.to_dict(rules=("-missions",)) for planet in planets], 200


api.add_resource(PlanetList, '/planets')

# make class for missions, post missions with response else error


class MissionList(Resource):
    def post(self):
        json = request.get_json()
        try:
            new_mission = Mission(
                json.get("name"), json.get("scientist_id"), json.get("planet_id"))
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        except ValueError:
            return {"errors": ["validation errors"]}, 400


api.add_resource(MissionList, '/missions')

# gets all scientists from API


class ScientistList(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [scientist.to_dict(rules=("-missions",)) for scientist in scientists], 200

# post to create new scientist, accepts name and field, returns error 400
    def post(self):
        json = request.get_json()
        try:
            new_scientist = Scientist(
                json.get("name"), json.get("field_of_study"))
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        except ValueError:
            return {"errors": ["validation errors"]}, 400


api.add_resource(ScientistList, '/scientists')

# gets individual scientist by ID with list of missions


class ScientistItem(Resource):
    def get(self, id):
        scientist = Scientist.query.get(id)
        if scientist:
            return scientist.to_dict()
        else:
            return {"error": "Scientist not found"}, 404

    # patch scientist with id, name, field_of_study
    def patch(self, id):
        json = request.get_json()
        scientist = Scientist.query.get(id)
        if not scientist:
            return {"error": "Scientist not found"}, 404

        try:
            if "name" in json:
                scientist.name = json["name"]

            if "field_of_study" in json:
                scientist.field_of_study = json["field_of_study"]

            db.session.commit()
            return scientist.to_dict(rules=("-missions",)), 202

        except ValueError:
            return {"errors": ["validation errors"]}, 400

    # delete scientist with id, return empty response body and http code

    def delete(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return {"error": "Scientist not found"}, 404
        db.session.delete(scientist)
        db.session.commit()
        return "", 204


api.add_resource(ScientistItem, '/scientists/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

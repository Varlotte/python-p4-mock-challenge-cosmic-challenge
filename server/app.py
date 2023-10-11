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


@app.route('/')
def home():
    return ''


# initialize flask restful
api = Api(app)


class ScientistList(Resource):
    def get(self):
        scientists_dict = [scientist.to_dict(
            rules=("-missions",)) for scientist in Scientist.query.all()]

        return make_response(scientists_dict, 200)

    def post(self):
        try:
            new_scientist = Scientist(
                name=request.json["name"],
                field_of_study=request.json["field_of_study"]
            )
            db.session.add(new_scientist)
            db.session.commit()

            return make_response(new_scientist.to_dict(rules=("-missions",)), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(ScientistList, "/scientists")


class ScientistItem(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()

        if scientist:
            return make_response(scientist.to_dict(), 200)
        else:
            return make_response({"error": "Scientist not found"}, 404)

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)

        try:
            for key in request.json:
                setattr(scientist, key, request.json[key])
            db.session.add(scientist)
            db.session.commit()

            return make_response(scientist.to_dict(rules=("-missions",)), 202)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)

        db.session.delete(scientist)
        db.session.commit()

        return make_response({}, 204)


api.add_resource(ScientistItem, "/scientists/<int:id>")


class PlanetList(Resource):
    def get(self):
        planets_dict = [planet.to_dict(rules=("-missions",))
                        for planet in Planet.query.all()]
        return make_response(planets_dict, 200)


api.add_resource(PlanetList, "/planets")


class MissionList(Resource):
    def post(self):
        try:
            new_mission = Mission(
                name=request.json["name"],
                scientist_id=request.json["scientist_id"],
                planet_id=request.json["planet_id"]
            )

            db.session.add(new_mission)
            db.session.commit()

            return make_response(new_mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(MissionList, "/missions")

if __name__ == '__main__':
    app.run(port=5555, debug=True)

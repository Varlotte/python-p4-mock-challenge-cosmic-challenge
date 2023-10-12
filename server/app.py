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
api = Api(app)


@app.route('/')
def home():
    return ''

# get /scientists from ScientistList with name, id, field_of_study, (-missions)
# post /scientists accepts name and field_of_study returns it with id (no missions) and 201 else 400 and message in readme


class ScientistList(Resource):
    def get(self):
        scientists_dict = [scientist.to_dict(
            rules=("-missions",)) for scientist in Scientist.query.all()]
        return make_response(scientists_dict, 200)

    def post(self):
        try:
            new_scientist = Scientist(
                name=request.json['name'],
                field_of_study=request.json['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(rules=("-missions",)), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(ScientistList, '/scientists')


# get /scientists/<int:id> with missions else 404 and message (paste from readme)
# patch /scientists/<int:id> accepts name and field, returns those with id and 202 else 400 and message in readme OR 404 if no id
# delete /scientists/<int:id> returns {} and 204 else 404

class ScientistItem(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return make_response(scientist.to_dict(), 200)
        else:
            return make_response({"error": "scientist not found"}, 404)

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


api.add_resource(ScientistItem, '/scientists/<int:id>')
# get /planets from PlanetList with id, name, distance, and nearest star (-missions)


class PlanetList(Resource):
    def get(self):
        planets_dict = [planet.to_dict(rules=('-missions',))
                        for planet in Planet.query.all()]
        return make_response(planets_dict, 200)


api.add_resource(PlanetList, '/planets')

# post /missions (takes name, scientist_id and planet_id) returns those and mission details else 400 and message in readme


class MissionItem(Resource):
    def post(self):
        try:
            new_mission = Mission(
                name=request.json['name'],
                scientist_id=request.json['scientist_id'],
                planet_id=request.json['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(MissionItem, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

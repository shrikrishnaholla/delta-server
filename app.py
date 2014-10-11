from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse
import redis

app = Flask(__name__)
api = restful.Api(app)

class User(restful.Resource):
    def get(self, email):
        r = redis.StrictRedis(host = 'localhost', port = 6379, db=0)
        if r.exists(email):
            return {'email': email, 'data': r.get(email)}
        else:
            return {}, 404

class UserList(restful.Resource):
    def post(self, email = None):
        if email is not None:
            restful.abort()

        parser = reqparse.RequestParser()
        parser.add_argument('email', type = str, required = True, location = 'form')
        parser.add_argument('first_name', required = True, location = 'form')
        parser.add_argument('title', required = True, location = 'form')

        args = parser.parse_args()

        user_email = args.get('email')
        user_data = args.get('data')

        r = redis.StrictRedis(host = 'localhost', port = 6379, db=0)
        if r.exists(user_email):
            return {'message':'User already exists'}, 200
        else:
            r.set(user_email, user_data)
            return {'email': user_email, 'data': r.get(user_email)}, 201

class Reco(restful.Resource):
    def get(self, email):
        r = redis.StrictRedis(host = 'localhost', port = 6379, db=0)
        if r.exists(email):
            rand_user = r.randomkey()
            while (rand_user == email):
                rand_user = r.randomkey()
            return {'email': rand_user, 'data': r.get(rand_user)}, 200
        else:
            return {'message': 'User does not exist'}, 400

api.add_resource(User, '/user/<string:email>')
api.add_resource(UserList, '/user')
api.add_resource(Reco, '/user/<string:email>/reco')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse
import redis
import json
import ast

app = Flask(__name__)
api = restful.Api(app)

def json_type(json_str):
    try:
        s = json.loads(json_str)
        return True
    except Exception, e:
        raise Exception("Improper data. Use JSON strings")

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
        parser.add_argument('data', type = json_type, required = True, location = 'form')

        args = parser.parse_args()

        user_email = args.get('email')
        user_data = args.get('data')

        r = redis.StrictRedis(host = 'localhost', port = 6379, db=0)
        if r.exists(user_email):
            return {'message':'User already exists'}, 200
        else:
            r.set(user_email, user_data)
            return {'email': user_email, 'data': r.get(user_email)}, 201

class RandReco(restful.Resource):
    def get(self, email):
        r = redis.StrictRedis(host = 'localhost', port = 6379, db = 0)
        if r.exists(email):
            rand_user = r.randomkey()
            while (rand_user == email):
                rand_user = r.randomkey()
            return {'email': rand_user, 'data': r.get(rand_user)}, 200
        else:
            return {'message': 'User does not exist'}, 400

class Reco(restful.Resource):

    def algorithm(self, user_email):
        try:
            # get data
            r = redis.StrictRedis(host = 'localhost', port = 6379, db = 0)
            user_data = r.get(user_email)
            print user_data
            print ast.literal_eval(user_data)

            # convert data to json
            user_data_json = json.loads(user_data)
            print 'created user_data_json'
            # get another random person
            for x in range(1, 30):
                rand_user_email = r.randomkey()
                print 'got rand_user_email' + str(rand_user_email)
                if rand_user_email == user_email:
                    continue
                print r.get(rand_user_email)
                rand_user_data = r.get(rand_user_email)
                rand_user_data_json = json.loads(r.get(rand_user_email))

                # if user and reco_user belong to the same bucket, do another rand
                if rand_user_data_json.get('bucket') is None:
                    continue
                if user_data_json.get('bucket') is None:
                    continue
                if rand_user_data_json['bucket'] == user_data_json['bucket']:
                    continue

                # if user and reco_user are connected, continue
                # TODO

                return rand_user_email
            return None
        except Exception, e:
            raise
            print e
            print user_email
            return None

    def get(self, email):
        r = redis.StrictRedis(host = 'localhost', port = 6379, db = 0)
        if r.exists(email):
            reco_user_email = self.algorithm(email)
            if reco_user_email is None:
                return 500
            return {'reco_user_email': reco_user_email, 'data': r.get(reco_user_email)}, 200
        else:
            return {'message': 'User does not exist'}, 400

api.add_resource(User, '/user/<string:email>')
api.add_resource(UserList, '/user')
api.add_resource(RandReco, '/user/<string:email>/rand')
api.add_resource(Reco, '/user/<string:email>/reco')

if __name__ == '__main__':
    app.run(debug=True)

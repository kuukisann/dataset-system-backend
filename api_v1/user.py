from api_v1 import app
from flask import Flask, abort, request, jsonify, make_response
from api_v1.model import create_session, User
import datetime
from flask_httpauth import HTTPBasicAuth
from flask import g

auth = HTTPBasicAuth()


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 400)


@auth.verify_password
def verify_password(username_or_token, password):
    try:
        # first try to authenticate by token
        print('verify_password\nuser_token = ', username_or_token, '\npassword = ', password)
        sess = create_session()
        data = User.verify_auth_token(username_or_token)
        print('verify_password\n', data)
        user = None
        if data:
            user = sess.query(User).filter(User.id == data['id']).first()
        if not user:
            # try to authenticate with username/password
            user = sess.query(User).filter(User.username == username_or_token).first()
            print('verify_password\n', user)
            if not user or not user.verify_password(password):
                return False
        g.user = user
        return True
    except Exception as e:
        print(e)
        return False


# @app.route('/api/v1.0/token')
# @g.auth.login_required
# def get_auth_token():
#     token = g.user.generate_auth_token()
#     return jsonify({'token': token.decode('ascii')})


@app.route('/api/v1.0/users', methods=['GET'])
@auth.login_required
def get_user_info():
    try:
        token = g.user.generate_auth_token()
        return jsonify({'code': 0, 'token': token.decode('ascii'), 'username': g.user.username, 'role': g.user.role})
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/users', methods=['POST'])
@auth.login_required
def create_user():
    try:
        if g.user.role != 'admin':
            return make_response(jsonify({'code': 1, 'error': 'permission denied'}), 401)
        new_user = []
        print(request.json['data'])

        for instance in request.json['data']:
            if len(instance['username']) > 255:
                return make_response(jsonify({'code': 1, 'error': 'username too long'}), 400)
            new_user.append(User(
                username=instance['username'],
                password=User.hash_password(instance['password']),
                role=instance['role'] if instance['role'] else 'user'
            ))
        sess = create_session()
        sess.add_all(new_user)
        sess.commit()
        return jsonify({'code': 0})
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1, 'error': 'repeated username'}), 400)


@app.route('/api/v1.0/users', methods=['PUT'])
@auth.login_required
def modify_user_info():
    try:
        print(request.json)

        password = request.json['data']['password']
        new_password = request.json['data']['newPassword']
        if g.user.verify_password(password):
            sess = create_session()
            sess.query(User).filter(User.id == g.user.id).first().password = User.hash_password(new_password)
            # g.user.password = User.hash_password(new_password)
            sess.commit()
            return jsonify({'code': 0})
        else:
            return make_response(jsonify({'code': 1, 'error': 'permission denied'}), 401)
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1, 'error': 'repeated username'}), 400)

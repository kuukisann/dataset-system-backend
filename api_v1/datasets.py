from api_v1 import app
from flask import Flask, abort, request, jsonify, make_response
from api_v1.model import create_session, DataSet, Resource
import datetime
from flask_httpauth import HTTPBasicAuth
from flask import g
from api_v1.user import auth
import pytz


@app.route('/api/v1.0/datasets', methods=['GET'])
@auth.login_required
def get_all_datasets():
    try:
        sess = create_session()
        offset = request.args.get('offset', default=0, type=int)
        limit = request.args.get('limit', default=10, type=int)
        ans_all = sess.query(DataSet).order_by(DataSet.id).all()
        ans = ans_all[offset:offset + limit]
        return jsonify({
            'code': 0,
            'maxLen': len(ans_all),
            'data': [x.serialize for x in ans]
        })
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 406)


@app.route('/api/v1.0/datasets', methods=['POST'])
@auth.login_required
def create_datasets():
    try:
        # print(request.json)
        if not request.json or 'data' not in request.json:
            make_response(jsonify({'code': 1}), 400)
        new_data_sets = []
        print(request.json['data'])

        for instance in request.json['data']:
            new_data_sets.append(DataSet(
                name=instance['name'],
                type=instance['type'],
                creator=g.user.username,
                createTime=datetime.datetime.now(tz=pytz.utc),
                modifyTime=datetime.datetime.now(tz=pytz.utc)
            ))
        sess = create_session()
        sess.add_all(new_data_sets)
        sess.commit()
        return jsonify({'code': 0})

    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/datasets/<int:datasetID>', methods=['GET'])
@auth.login_required
def get_dataset(datasetID):
    try:
        sess = create_session()
        ans = sess.query(DataSet).filter(DataSet.id == datasetID).first()
        print(ans)
        if ans:
            return jsonify({'code': 0, 'data': ans.serialize})
        else:
            return make_response(jsonify({'code': 1}), 404)
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/datasets/<int:datasetID>', methods=['DELETE'])
@auth.login_required
def delete_dataset(datasetID):
    try:
        sess = create_session()
        sess.query(DataSet).filter(DataSet.id == datasetID).delete()
        sess.commit()
        return jsonify({'code': 0})
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/datasets/<int:datasetID>', methods=['PUT'])
@auth.login_required
def update_dataset(datasetID):
    try:
        # print(request.json)
        if not request.json or 'data' not in request.json:
            make_response(jsonify({'code': 1}), 400)
        print(request.json['data'])

        sess = create_session()
        ans = sess.query(DataSet).filter(DataSet.id == datasetID).first()

        if ans:
            modify_flag = False
            if request.json['data']['name']:
                ans.name = request.json['data']['name']
                modify_flag = True
            if modify_flag:
                ans.modifyTime = datetime.datetime.now(tz=pytz.utc)
            sess.commit()
            return jsonify({'code': 0})
        else:
            return make_response(jsonify({'code': 1}), 400)

    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)

from api_v1 import app
from flask import Flask, abort, request, jsonify, make_response
from api_v1.model import create_session, DataSet, Resource
from sqlalchemy import and_
import datetime
from flask_httpauth import HTTPBasicAuth
from flask import g
from api_v1.user import auth
import pytz
import api_v1.tools as tools


@app.route('/api/v1.0/datasets/<int:datasetID>/resources', methods=['GET'])
@auth.login_required
def get_all_resources(datasetID):
    try:
        sess = create_session()
        data_set = sess.query(DataSet).filter(DataSet.id == datasetID).first()
        print(data_set)
        if data_set:
            offset = request.args.get('offset', default=0, type=int)
            limit = request.args.get('limit', default=10, type=int)
            ans_all = data_set.resources
            print(len(ans_all))
            ans = ans_all[offset:offset + limit]
            return jsonify({
                'code': 0,
                'maxLen': len(ans_all),
                'data': [x.serialize for x in ans]
            })
        else:
            return make_response(jsonify({'code': 1}), 404)
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/datasets/<int:datasetID>/resources', methods=['POST'])
@auth.login_required
def create_resources(datasetID):
    try:
        new_res = []

        # 上传的是id
        if request.json['type'] == 'text':
            for instance in request.json['data']:
                new_res.append(Resource(
                    dataSetID=datasetID,
                    src=instance['src'],
                    environment=instance['environment'],
                    fileMsg=instance['fileMsg'],
                    filename=instance['filename'],
                    ifPositive=instance['ifPositive'],
                    nameExtension=instance['nameExtension'],
                    type=instance['type'],
                    createTime=datetime.datetime.now(tz=pytz.utc),
                    modifyTime=datetime.datetime.now(tz=pytz.utc)
                ))
            sess = create_session()
            sess.add_all(new_res)
            sess.commit()
            return jsonify({'code': 0})

        # 上传的是文件，将由服务器上传给远端
        if request.json['type'] == 'file':
            # print(request.json)
            for instance in request.json['data']:
                src = tools.upload_file(instance['content'])
                new_res.append(Resource(
                    dataSetID=datasetID,
                    src=src,
                    environment=instance['environment'],
                    fileMsg=instance['fileMsg'],
                    filename=instance['filename'],
                    ifPositive=instance['ifPositive'],
                    nameExtension=instance['nameExtension'],
                    type=instance['type'],
                    createTime=datetime.datetime.now(tz=pytz.utc),
                    modifyTime=datetime.datetime.now(tz=pytz.utc)
                ))
            sess = create_session()
            sess.add_all(new_res)
            sess.commit()
            return jsonify({'code': 0})

        return jsonify({'code': 1}, 400)

    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/datasets/<int:datasetID>/resources/<int:srcID>', methods=['GET'])
@auth.login_required
def get_resource_info(datasetID, srcID):
    try:
        sess = create_session()
        res = sess.query(Resource).filter(and_(Resource.dataSetID == datasetID, Resource.id == srcID)).first()
        print(res)
        if res:
            return jsonify({
                'code': 0,
                'data': res.serialize
            })
        else:
            return make_response(jsonify({'code': 1}), 404)
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/datasets/<int:datasetID>/resources/<int:srcID>', methods=['DELETE'])
@auth.login_required
def delete_resource(datasetID, srcID):
    try:
        sess = create_session()
        res = sess.query(Resource).filter(and_(Resource.dataSetID == datasetID, Resource.id == srcID)).first()
        print(res)
        if res:
            sess.delete(res)
            sess.commit()
            return jsonify({'code': 0})
        else:
            return make_response(jsonify({'code': 1}), 406)
    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)


@app.route('/api/v1.0/datasets/<int:datasetID>/resources/<int:srcID>', methods=['PUT'])
@auth.login_required
def update_resource(datasetID, srcID):
    try:
        # print(request.json)
        print(request.json['data'])

        sess = create_session()
        res = sess.query(Resource).filter(and_(Resource.dataSetID == datasetID, Resource.id == srcID)).first()

        if res:
            modify_flag = False
            if request.json['data']['environment']:
                res.environment = request.json['data']['environment']
                modify_flag = True
            if request.json['data']['fileMsg']:
                res.fileMsg = request.json['data']['fileMsg']
                modify_flag = True
            if request.json['data']['filename']:
                res.filename = request.json['data']['filename']
                modify_flag = True
            if request.json['data']['ifPositive']:
                res.ifPositive = request.json['data']['ifPositive']
                modify_flag = True
            if request.json['data']['nameExtension']:
                res.nameExtension = request.json['data']['nameExtension']
                modify_flag = True
            if request.json['data']['src']:
                res.src = request.json['data']['src']
                modify_flag = True
            if request.json['data']['type']:
                res.type = request.json['data']['type']
                modify_flag = True

            if modify_flag:
                res.modifyTime = datetime.datetime.now(tz=pytz.utc)
            sess.commit()
            return jsonify({'code': 0})
        else:
            return make_response(jsonify({'code': 1}), 400)

    except Exception as e:
        print(e)
        return make_response(jsonify({'code': 1}), 400)

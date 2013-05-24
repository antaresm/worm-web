# -*- coding: utf-8
import json
import datetime

from django.http import HttpResponse
from utils.utils import *
from django.contrib.auth.models import User


def update_token(id):
    token = User.objects.make_random_password()
    sql = 'UPDATE wusers SET token = "' + token + '" WHERE id = ' + str(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    db.close()
    return token


def exist_user(login, password):
    sql = 'SELECT id as id, password as pwd FROM wusers WHERE login like "' + login + '"'
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    if len(data) == 0:
        return 0
    else:
        if data[0][1] == password or password == '':
            return data[0][0]
        else:
            return -1


def exist_user_id(id):
    sql = 'SELECT count(id) as count FROM wusers WHERE id = ' + str(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return data[0][0] > 0


def user_token(id):
    sql = 'SELECT token as count FROM wusers WHERE id = ' + str(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return data[0][0]


def check_token(id, token):
    sql = 'SELECT token FROM wusers WHERE id = ' + str(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    db.close()
    return data['token'] == token


def registration(data):
    if data:
        j_data = json.loads(data)
        sql = 'INSERT INTO wusers ('

        for fName in j_data:
            if fName != u'id' and fName != u'lastUpdate':
                sql += fName + ','
        sql = sql[:-1] + ') VALUES ('

        for fieldName in j_data:
            value = j_data[fieldName]
            value = unicode(value)
            sql += '"' + value + '",'
        sql = sql[:-1] + ')'

        db = get_db()
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()

        result_data = dict()
        result_data['id'] = cursor.lastrowid

        result = dict()
        # All ok )
        result['code'] = 200
        result['data'] = result_data

        return json.dumps(result)
    else:
        result = dict()
        result['code'] = 401
        result['message'] = 'Empty data'
        return json.dumps(result)


def login(login, password):
    id = exist_user(login, password)
    if id > 0:
        token = update_token(id)
        result_data = dict()
        result_data['id'] = id
        result_data['token'] = token
        result = dict()
        result['code'] = 200
        result['data'] = result_data
        return json.dumps(result)
    else:
        result = dict()
        result['code'] = 401
        result['message'] = 'Incorrect data or password'
        return json.dumps(result)


def user_data(id, token):
    if exist_user_id(id) > 0:
        if user_token(id) == token:
            db = get_db()
            cursor = db.cursor()
            sql = 'SELECT * FROM wusers'
            cursor.execute(sql)
            data = cursor.fetchall()
            result_data = dbdata_tojson('wusers', data)
            db.close()

            result = dict()
            result['code'] = 200
            result['data'] = result_data

            return json.dumps(result)
        else:
            result = dict()
            result['code'] = 401
            result['message'] = 'Incorrect token'
            return json.dumps(result)
    else:
        result = dict()
        result['code'] = 401
        result['message'] = 'User not found'
        return json.dumps(result)


def update(id, token, data):
    if exist_user_id(id):
        if user_token(id) == token:
            j_data = json.loads(data)

            sql = 'UPDATE wusers SET '
            for fName in j_data:
                if fName != 'login':
                    sql += fName + ' = "' + j_data[fName] + '",'
            sql = sql[:-1] + ' WHERE id = ' + str(id)
            db = get_db()
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            db.close()

            result = dict()
            result['code'] = 200
            return json.dumps(result)
        else:
            result = dict()
            result['code'] = 401
            result['message'] = 'Incorrect token'
            return json.dumps(result)
    else:
        result = dict()
        result['code'] = 401
        result['message'] = 'User not found'
        return json.dumps(result)


# Main request method
# Check action type and call method
def main(request, id=0, token=""):
    # Если это метод POST - это однозначно создание новой записи
    if 'POST' == request.method:
        return HttpResponse(registration(request.body))

    # Если это метод GET
    elif 'GET' == request.method:
        # Если нам передан id и экшн login
        username = ""
        password = ""
        if "username" in request.GET:
            username = request.GET["username"]
        if "password" in request.GET:
            password = request.GET["password"]
        if username != "" and password != "":
            return HttpResponse(login(username, password))
        elif id > 0 and token != "":
            return HttpResponse(user_data(id, token))
    elif 'PUT' == request.method:
        return HttpResponse(update(id, token, request.body))

    # Либо возвращает что метод запроса не верный
    return HttpResponse('Incorrect method')
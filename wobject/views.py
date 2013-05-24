# -*- coding: utf-8
from django.http import HttpResponse
import json
from utils.utils import *


def empty(request):
    return HttpResponse('Hello WORM!')


def create(name, data):
    if data:
        j_data = json.loads(data)
        sql = 'INSERT INTO ' + name + ' ('

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


def read(name, id):
    db = get_db()
    cursor = db.cursor()
    sql = 'SELECT * FROM ' + name + ' WHERE id = ' + str(id)
    cursor.execute(sql)
    data = cursor.fetchall()
    result_data = dbdata_tojson(name, data, False)
    db.close()

    result = dict()
    result['code'] = 200
    result['data'] = result_data
    return json.dumps(result)


def delete(name, id):
    db = get_db()
    cursor = db.cursor()
    sql = 'DELETE FROM ' + name + ' WHERE id = ' + str(id)
    cursor.execute(sql)
    db.commit()
    db.close()

    result = dict()
    result['code'] = 200
    return json.dumps(result)


def update(name, id, data):
    j_data = json.loads(data)
    sql = 'UPDATE ' + name + ' SET '
    for fName in j_data:
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


def select(name, params=''):
    db = get_db()
    cursor = db.cursor()
    sql = 'SELECT * FROM ' + name
    if params != '':
        sql += ' WHERE ' + params
    cursor.execute(sql)
    data = cursor.fetchall()
    result_data = dbdata_tojson(name, data)
    db.close()

    result = dict()
    result['code'] = 200
    result['data'] = result_data
    return json.dumps(result)


# Метод основной обработки запросов
# Тут мы проверяем что мы должны сделать и куда перенаправить обработку
def main(request, name='', id=0):
    # Если это метод POST - это однозначно создание новой записи
    if 'POST' == request.method:
        return HttpResponse(create(name, request.body))

    # Если это метод GET
    elif 'GET' == request.method:
        # Если нам передан id сущности значит надо ее получить
        if id > 0:
            return HttpResponse(read(name, id))

        # Иначе нам надо сделать выборку нескольких сущностей
        else:
            if 'where' in request.GET:
                wparams = request.GET['where']
            else:
                wparams = ''
            return HttpResponse(select(name, wparams))

    # Если это метод PUT значит надо обновить сущность
    elif 'PUT' == request.method:
        return HttpResponse(update(name, id, request.body))

    # Если метод запроса DELETE то мы удаляем сущность
    elif 'DELETE' == request.method:
        return HttpResponse(delete(name, id))

    # Либо возвращает что метод запроса не верный
    return HttpResponse('Incorrect method')

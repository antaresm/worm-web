# -*- coding: utf-8
from django.http import HttpResponse
import json
import MySQLdb


def empty(request):
    return HttpResponse('Hello WORM!')


def password():
    return "u97jcbj6Gkgcg3H"
    #return ""


def get_db():
    return MySQLdb.connect(host="localhost", user="root", passwd=password(), db="worm", charset='utf8')


def get_table_schema(table_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("describe " + table_name)
    result = cursor.fetchall()
    db.close()
    return result


def dbdata_tojson(t_name, db_data, allData=True):
    result_data = []
    result_row = dict()
    schema = get_table_schema(t_name)
    field_num = 0
    for row in db_data:
        for value in row:
            if value.__class__.__name__ == 'datetime':
                value = str(value)
            field_name = schema[field_num][0]
            field_num += 1
            result_row[field_name] = value
        if not allData:
            return result_row
        else:
            result_data.append(result_row)
            field_num = 0
    return result_data


def create(name, data):
    if data:
        j_data = json.loads(data)
        sql = 'INSERT INTO ' + name + ' ('

        for fName in j_data:
            if fName != u'id' and fName != u'lastUpdate':
                sql += fName + ','
        sql = sql[:-1]


        sql = sql + ') VALUES ('

        for fieldName in j_data:
            sql += '"' + str(j_data[fieldName]) + '",'
        sql = sql[:-1]
        sql = sql + ')'

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
        sql += fName + ' = "' + str(j_data[fName]) + '",'
    sql = sql[:-1]
    sql += ' WHERE id = ' + str(id)
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

# -*- coding: utf-8
from django.http import HttpResponse
import json, datetime
from models import WUser
from django.contrib.auth.models import User


def registration(data):
    if data:
        j_data = json.loads(data)
        try:
            WUser.objects.get(username=j_data["username"])
            result = dict()
            result['code'] = 401
            result['message'] = 'Username already exist'
            return json.dumps(result)

        except WUser.DoesNotExist:
            user = WUser()
            user.username = j_data["name"]
            user.password = j_data["password"]
            user.email = j_data["email"]
            user.avatar = j_data["avatar"]
            user.token = User.objects.make_random_password()
            user.token_time = datetime.datetime.now()
            user.save()

            result_data = dict()
            result_data['id'] = user.id
            result_data['token'] = user.token
            result = dict()
            result['code'] = 200
            result['data'] = result_data

            return json.dumps(result)
    else:
        result = dict()
        result['code'] = 401
        result['message'] = 'Empty data'
        return json.dumps(result)


def login(request):
    return ""


# Метод основной обработки запросов
# Тут мы проверяем что мы должны сделать и куда перенаправить обработку
def main(request, id=0):
    # Если это метод POST - это однозначно создание новой записи
    if 'POST' == request.method:
        return HttpResponse(registration(request.body))

    # Если это метод GET
    elif 'GET' == request.method:
        # Если нам передан id сущности значит надо ее получить
        if id > 0:
            return ""#HttpResponse(read(name, id))

        # Иначе нам надо сделать выборку нескольких сущностей
        else:
            if 'where' in request.GET:
                wparams = request.GET['where']
            else:
                wparams = ''
            return ""#HttpResponse(select(name, wparams))

    # Либо возвращает что метод запроса не верный
    return HttpResponse('Incorrect method')
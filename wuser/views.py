# -*- coding: utf-8
from django.http import HttpResponse
import json, datetime
from models import WUser
from django.contrib.auth.models import User
from django.contrib import auth


def registration(data):
    if data:
        j_data = json.loads(data)
        username = j_data["name"]
        try:
            WUser.objects.get(username=username)
            result = dict()
            result['code'] = 401
            result['message'] = 'Username already exist'
            return json.dumps(result)

        except WUser.DoesNotExist:
            user = WUser()
            user.username = j_data["name"]
            user.set_password(j_data["password"])
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


def login(username, password):
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        wuser = WUser.objects.get(user_ptr_id=user.id)
        wuser.token = User.objects.make_random_password()
        wuser.token_time = datetime.datetime.now()
        wuser.save()

        result_data = dict()
        result_data['id'] = wuser.id
        result_data['token'] = wuser.token
        result = dict()
        result['code'] = 200
        result['data'] = result_data
        return json.dumps(result)
    else:
        result = dict()
        result['code'] = 401
        result['message'] = 'Incorrect data or password'
        return json.dumps(result)


# Метод основной обработки запросов
# Тут мы проверяем что мы должны сделать и куда перенаправить обработку
def main(request):
    # Если это метод POST - это однозначно создание новой записи
    if 'POST' == request.method:
        return HttpResponse(registration(request.body))

    # Если это метод GET
    elif 'GET' == request.method:
        # Если нам передан id и экшн login
        username = request.GET["username"]
        password = request.GET["password"]
        if username != "" and password != "":
            return HttpResponse(login(username, password))

    # Либо возвращает что метод запроса не верный
    return HttpResponse('Incorrect method')
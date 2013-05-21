# -*- coding: utf-8
from django.http import HttpResponse
import json
import datetime
from django.core import serializers
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


def user_data(id, token):
    try:
        wu = WUser.objects.get(id=id)
        if wu.token == token:
            result = dict()
            result['code'] = 200
            result['data'] = serializers.serialize('json', [wu])
            return json.dumps(result)
        else:
            result = dict()
            result['code'] = 401
            result['message'] = 'Incorrect token'
            return json.dumps(result)
    except WUser.DoesNotExist:
        result = dict()
        result['code'] = 401
        result['message'] = 'User not founded'
        return json.dumps(result)


def update(id, token, data):
    try:
        wu = WUser.objects.get(id=id)
        if wu.token == token:
            j_data = json.loads(data)

            if 'email' in j_data:
                wu.email = j_data['email']
            if 'password' in j_data:
                wu.set_password(j_data['password'])
            if 'avatar' in j_data:
                wu.avatar = j_data['avatar']
            wu.save()

            result = dict()
            result['code'] = 200
            return json.dumps(result)
        else:
            result = dict()
            result['code'] = 401
            result['message'] = 'Incorrect token'
            return json.dumps(result)
    except WUser.DoesNotExist:
        result = dict()
        result['code'] = 401
        result['message'] = 'User not founded'
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
import json

from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.db.models import Q

from models import *

def test(request):
    return HttpResponse(json.dumps({'you-lost': 'the-game'}))

def add_user(request):
    try:
        display_name = request.GET['display_name']
        unique_name = request.GET['unique_name']
        User.objects.create(display_name=display_name, unique_name=unique_name)
        return HttpResponse(json.dumps({'result': 'success'}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except IntegrityError as e:
        return HttpResponse(json.dumps({'result': 'unique name exists'}))

def add_relationship(request):
    try:
        first_user_name = request.GET['first_user']
        second_user_name = request.GET['second_user']
        first_user = User.objects.get(unique_name=first_user_name)
        second_user = User.objects.get(unique_name=second_user_name)
        Relationship.objects.create(first_user=first_user.id, second_user=second_user.id)
        return HttpResponse(json.dumps({'result': 'success'}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))

def show_friends(request):
    try:
        unique_name = request.GET['unique_name']
        user = User.objects.get(unique_name=unique_name)
        relationships = Relationship.objects.filter(Q(first_user=user.id) | Q(second_user=user.id))
        return HttpResponse(json.dumps({'result': 'success', 'data': map(lambda x: {'display_name': User.objects.get(id=x.first_user).display_name}, relationships)}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))

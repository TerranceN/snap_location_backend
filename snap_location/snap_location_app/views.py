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
        min_id = min(first_user.id, second_user.id)
        max_id = max(first_user.id, second_user.id)
        Relationship.objects.create(first_user=min_id, second_user=max_id)
        return HttpResponse(json.dumps({'result': 'success'}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except IntegrityError as e:
        return HttpResponse(json.dumps({'result': 'success'}))

def show_friends(request):
    try:
        unique_name = request.GET['unique_name']
        user = User.objects.get(unique_name=unique_name)
        relationships = Relationship.objects.filter(Q(first_user=user.id) | Q(second_user=user.id))
        def get_relation_data(relation):
            other_user = None
            if (relation.first_user == user.id):
                other_user = User.objects.get(id=relation.second_user)
            else:
                other_user = User.objects.get(id=relation.first_user)
            return {'display_name': other_user.display_name}
        return HttpResponse(json.dumps({'result': 'success', 'data': map(get_relation_data, relationships)}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))

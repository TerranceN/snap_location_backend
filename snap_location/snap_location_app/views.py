import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.db.models import Q

from datetime import datetime

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
        first_user = User.objects.get(unique_name=first_user_name.lower())
        second_user = User.objects.get(unique_name=second_user_name.lower())
        min_id = min(first_user.id, second_user.id)
        max_id = max(first_user.id, second_user.id)
        Relationship.objects.create(first_user=min_id, second_user=max_id)
        return HttpResponse(json.dumps({'result': 'success'}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'add_info': e.message}))
    except IntegrityError as e:
        # this means the relationship already exists, so might as well return success
        return HttpResponse(json.dumps({'result': 'success'}))
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

def show_friends(request):
    try:
        unique_name = request.GET['unique_name']
        user = User.objects.get(unique_name=unique_name.lower())
        relationships = Relationship.objects.filter(Q(first_user=user.id) | Q(second_user=user.id))
        def get_relation_data(relation):
            other_user = None
            if (relation.first_user == user.id):
                other_user = User.objects.get(id=relation.second_user)
            else:
                other_user = User.objects.get(id=relation.first_user)
            return {'display_name': other_user.display_name, 'unique_name': other_user.unique_name_display}
        return HttpResponse(json.dumps({'result': 'success', 'data': map(get_relation_data, relationships)}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

def push_image_location(request):
    try:
        unique_name = request.POST['unique_name']
        recipients_names = request.POST.getlist('recipients')
        image = request.FILES['image']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))

    try:
        user = User.objects.get(unique_name=unique_name.lower())
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

    try:
        recipients = map(lambda x: User.obects.get(unique_name=x.lower()), recipients_names)
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return HttpResponse(json.dumps({'result': 'can\'t convert lat/long data to float', 'add_info': e.message}))

    uploaded_image = UploadedImage.objects.create(reference_count=len(recipients), image_data=image)
    for recipient in recipients:
        GameRound.objects.create(
                sender=user.id,
                recipient=recipient.id,
                datetime=datetime.now(),
                gps_latitude=latitude,
                gps_longitude=longitude
            )

    return HttpResponse(json.dumps({'result': 'success'}))

def file_upload_test(request):
    return render_to_response('file_upload.html', {}, context_instance=RequestContext(request))

def upload_file(request):
    print request.POST
    return HttpResponse(json.dumps({'result': 'success', 'files': map(lambda x: request.FILES[x].name, request.FILES)}))

def get_users(request):
    return HttpsResponse(json.dumps({'result': 'success'}))

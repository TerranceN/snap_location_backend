import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.db.models import Q

from datetime import datetime

from models import *

from math import *

def test(request):
    return HttpResponse(json.dumps({'you-lost': 'the-game'}))

def add_user(request):
    try:
        display_name = request.POST['display_name']
        unique_name = request.POST['unique_name']
        User.objects.create(display_name=display_name, unique_name=unique_name)
        return HttpResponse(json.dumps({'result': 'success'}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except IntegrityError as e:
        return HttpResponse(json.dumps({'result': 'unique name exists'}))

def add_relationship(request):
    try:
        first_user_name = request.POST['first_user']
        second_user_name = request.POST['second_user']
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
        unique_name = request.POST['unique_name']
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
        print unique_name
        user = User.objects.get(unique_name=unique_name.lower())
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

    try:
        print recipients_names
        recipients = map(lambda x: User.objects.get(unique_name=x.lower()), recipients_names)
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
                image_data=uploaded_image.id,
                datetime=datetime.now(),
                gps_latitude=latitude,
                gps_longitude=longitude
            )

    return HttpResponse(json.dumps({'result': 'success'}))

def file_upload_test(request):
    return render_to_response('file_upload.html', {}, context_instance=RequestContext(request))

def upload_file(request):
    return HttpResponse(json.dumps({'result': 'success', 'files': map(lambda x: request.FILES[x].name, request.FILES)}))

def get_users(request):
    user_data = map(lambda x: {'unique_name': x.unique_name_display}, User.objects.all())
    return HttpResponse(json.dumps({'result': 'success', 'users': user_data}))

def upload_game_round(request):
    return render_to_response('upload_game_round.html', {}, context_instance=RequestContext(request))

def make_user(request):
    return render_to_response('make_user.html', {}, context_instance=RequestContext(request))

def get_gamedata(request):
    game_rounds = map(lambda x: {
        'sender': User.objects.get(id=x.sender).unique_name_display,
        'recipient': User.objects.get(id=x.recipient).unique_name_display,
        'image': str(x.image_data),
        'latitude': str(x.gps_latitude),
        'longitude': str(x.gps_longitude),
        'datetime': str(x.datetime)
        },
            GameRound.objects.all())
    return HttpResponse(json.dumps({'result': 'success', 'game_rounds': game_rounds}))

def guess_location(request):
    try:
        unique_name = request.GET['unique_name']
        sender_name = request.GET['friend_name']
        guess_lat = float(request.GET['guess_lat'])
        guess_lon = float(request.GET['guess_lon'])

        user = User.objects.get(unique_name=unique_name.lower())
        sender = User.objects.get(unique_name=sender_name.lower())
        game_round = GameRound.objects.filter(sender=sender.id, recipient=user.id).order_by('datetime')[:1].get()
        image = UploadedImage.objects.get(id=game_round.image_data)
        image_lat = game_round.gps_latitude
        image_lon = game_round.gps_longitude
        distance = get_distance(image_lat, image_lon, guess_lat, guess_lon)

        # Commented for testing purposes
        # game_round.delete()
        # image.reference_count -= 1
        # image.save()
        # if image.reference_count == 0:
            # image.delete()

        score = float(10000)/distance if distance!=0 else 1000
        return HttpResponse(json.dumps({'result': 'success', 'score': score}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except (User.DoesNotExist, GameRound.DoesNotExist) as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))


def get_distance(lat1, lon1, lat2, lon2):
    # use +/- to indicate north/south and east/west
    # using pythagorean for now, can use great circle distance later
    r = 6371
    dy = (lat2 - lat1) * pi / 180 * r
    dx = (lon2 - lon1) * pi / 180 * r * cos(lat1 * pi / 180)
    return sqrt(dx**2 + dy**2)

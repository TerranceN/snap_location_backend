import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.db.models import Q, FileField
from django.core.files.base import ContentFile, File

from datetime import datetime
import tempfile

from models import *

from math import *

def test(request):
    return HttpResponse(json.dumps({'you-lost': 'the-game'}))

def get_profile(request):
    try:
        unique_name = request.POST['unique_name']
        user = User.objects.get(unique_name=unique_name.lower())
        return HttpResponse(json.dumps({'result': 'success', 'display_name': display_name, 'unique_name_display': unique_name_display, 'score': score, 'images_sent': images_sent, 'images_received': images_received}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

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
            rounds = GameRound.objects.filter(sender=other_user.id, recipient=user.id)
            return {'display_name': other_user.display_name, 'unique_name': other_user.unique_name_display, 'score': other_user.score, 'num_rounds_pending': len(rounds)}
        return HttpResponse(json.dumps({'result': 'success', 'data': map(get_relation_data, relationships)}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

def push_image_location(request):
    try:
        unique_name = request.POST['unique_name']
        recipients_names = request.POST.getlist('recipients')
        image_data = request.POST['image']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))

    try:
        user = User.objects.select_for_update().get(unique_name=unique_name.lower())
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

    try:
        recipients = map(lambda x: User.objects.get(unique_name=x.lower()), recipients_names)
    except User.DoesNotExist as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

    sent = 0
    for i in range(len(recipients)):
        sent += 1.0/(i+1)
    user.images_sent += int(round(sent))
    user.save()

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return HttpResponse(json.dumps({'result': 'can\'t convert lat/long data to float', 'add_info': e.message}))

    tmp = tempfile.TemporaryFile()
    try:
        tmp.write(image_data)
        uploaded_image = UploadedImage.objects.create(reference_count = len(recipients), image_data=File(tmp))
    except Exception, e:
        import traceback
        return HttpResponse(json.dumps({'result': 'tempfile error', 'add_info': e.message, 'stacktrace': traceback.format_exc()}))
    finally:
        tmp.close()
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

def make_relationship(request):
    return render_to_response('make_relationship.html', {}, context_instance=RequestContext(request))

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

def get_images(request):
    urls = map(lambda x: x.image_data.url, UploadedImage.objects.all())
    return HttpResponse(json.dumps({'result': 'success', 'images': urls}))

def get_relationships(request):
    relationships = map(lambda x: {
            'first_user': User.objects.get(id=x.first_user).unique_name,
            'second_user': User.objects.get(id=x.second_user).unique_name},
        Relationship.objects.all())
    return HttpResponse(json.dumps({'result': 'success', 'relationships': relationships}))

def guess_location(request):
    try:
        unique_name = request.POST['unique_name']
        sender_name = request.POST['friend_name']
        guess_lat = 45.
        guess_lon = 45.

        user = User.objects.select_for_update().get(unique_name=unique_name.lower())
        sender = User.objects.select_for_update().get(unique_name=sender_name.lower())
        game_rounds = GameRound.objects.filter(sender=sender.id, recipient=user.id).order_by('datetime')[:2]
        current_round = game_rounds[0]
        image = UploadedImage.objects.select_for_update().get(id=current_round.image_data)
        image_lat = current_round.gps_latitude
        image_lon = current_round.gps_longitude
        distance = get_distance(image_lat, image_lon, guess_lat, guess_lon)

        # Commented for testing purposes
        # current_round.delete()
        # image.reference_count -= 1
        # image.save()
        # if image.reference_count == 0:
            # image.delete()

        sender.score += 5
        sender.save()

        user.images_received += 1
        ratio = float(user.images_sent)/user.images_received
        if ratio < 0.4:
            ratio = 0.4
        elif ratio > 2.5:
            ratio = 2.5

        if distance < 0.05:
            score = 15
        elif distance < 0.1:
            score = 10
        elif distance < 0.3:
            score = 7
        elif distance < 0.5:
            score = 5
        elif distance < 1:
            score = 3
        else:
            score = 2
        score = int(round(ratio*score))
        user.score += score
        user.save()

        d = {'result': 'success', 'score': score, 'correct_lat': image_lat, 'correct_lon': image_lon, 'distance': distance}
        if len(game_rounds) > 1:
            next_round = game_rounds[1]
            image = UploadedImage.objects.get(id=next_round.image_data)
            url = image.image_data.url
            d['next_url'] = url
        return HttpResponse(json.dumps(d))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except (User.DoesNotExist, GameRound.DoesNotExist, UploadedImage.DoesNotExist) as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

def get_image(request):
    try:
        unique_name = request.POST['unique_name']
        sender_name = request.POST['friend_name']

        user = User.objects.get(unique_name=unique_name.lower())
        sender = User.objects.get(unique_name=sender_name.lower())
        game_round = GameRound.objects.filter(sender=sender.id, recipient=user.id).order_by('datetime')[:1].get()
        image = UploadedImage.objects.get(id=game_round.image_data)
        url = image.image_data.url

        return HttpResponse(json.dumps({'result': 'success', 'url': url}))
    except MultiValueDictKeyError as e:
        return HttpResponse(json.dumps({'result': 'missing arguments', 'long_error': e.message}))
    except (User.DoesNotExist, GameRound.DoesNotExist, UploadedImage.DoesNotExist) as e:
        return HttpResponse(json.dumps({'result': 'unknown user', 'add_info': e.message}))

def get_distance(lat1, lon1, lat2, lon2):
    r = 6371
    # use pythagorean method if distances are small to avoid roundoff errors
    if abs(lat2 - lat1) < 0.1 and abs(lon2 - lon1) < 0.1:
        dy = rad(lat2 - lat1) * r
        dx = rad(lon2 - lon1) * r * cos(rad(lat1))
        return sqrt(dx**2 + dy**2)
    else:
        return r * acos(sin(rad(lat1))*sin(rad(lat2)) + cos(rad(lat1))*cos(rad(lat2))*cos(rad(lon2-lon1)))

def rad(angle):
    return angle * pi / 180

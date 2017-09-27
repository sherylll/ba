# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import LED, Person, Publisher
from django.contrib.auth.models import User, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.middleware.csrf import get_token
from .forms import *

from django.core.exceptions import PermissionDenied
from AESMAC import decrypt_final
import os
import uuid
# Create your views here.

def get_keys(uid):
    users = User.objects.all()
    uid_and_keys = ["uid",]
    for u in users:
        if u.person.uid == uid:
            uid_and_keys = u.person.keys.split(',')
            break
    return uid_and_keys[1:]
 
def auth_from_url(authString, request):

    uid = authString[:8]
    encrypted = authString[8:]    
    username = request.user.username

    keys = get_keys(uid)

    user_object = None
    #if no keys found return empty user object
    if  len(keys) == 0:
        return user_object
    
    #user not logged in and wants to be logged in
    if not username and encrypted != '' :
        sessionID = Publisher.objects.get(name = 'publisher').sessionID
        print 'sesssionID is '+sessionID
        login_info = decrypt_final(keys, str(encrypted), sessionID)

        """cheating here...
        """
        if login_info == "lol":
            login_info = decrypt_final(keys, str(encrypted), "sessionID")
        [u, p] = login_info.split(',')
        #print "DEBUGGING...\n"
        #print u, p
        user_object = authenticate(username = u, password = p)
        print "DEBUGGING...\n"
        print user_object
        username = user_object.username
        if username is not None:
           login(request, user_object)
    return user_object
    

def aes_hmac_verified(function):

    #kwargs = {}
    def wrap(request, *args, **kwargs):
        username = None

        if request.method == 'POST':
            data = request.POST
            auth_from_url(data['auth_str'], request)
        
        #if not logged in
        if not request.user.has_perm('devices.led_view'):
            path = request.path
            offset = path.find('devices') + 8
            authString = path[offset:]
        
            usr_obj = auth_from_url(authString, request)
            if usr_obj:
                username = usr_obj.username
        else:
            #already logged in
            username = request.user.username
        if not username:
            raise PermissionDenied
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap        

def superuser_required(function):
    def wrap(request, *args, **kwargs):
        print request.POST
        authString = request.POST['auth_str']    
        if not request.user:
            if not auth_from_url(authString, request).is_superuser:
                raise PermissionDenied
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap       
   
#@aes_hmac_verified    
def index(request):
    
    #for display
    username = request.user.username
    #if not username:
    #    return redirect('/login/')
    devices = LED.objects.all()
    print devices[0].name
    #state = devices[0].read_led()
       
    response = render(request, 'index.html', locals())
    return response
    
@aes_hmac_verified
def led(request):    
    if not request.user.has_perm('devices.led_view'):
        return redirect('/login/')
   
    if request.method == 'GET':
        state = request.path[-1]
        hotplate_nr = request.path[-3]
        #print hotplate_nr
        #print request.user.username
        perm_on = request.user.has_perm('devices.led_on')
        perm_off = request.user.has_perm('devices.led_off')

        print request.user

        # Check if the led state is 0 (off) or 1 (on) and set the LED accordingly.
        try:
            if not int(hotplate_nr) in range(10):
                pass
            hotplate_name = 'Hotplate '+ hotplate_nr
            print hotplate_name
            hp = LED.objects.get(name = hotplate_name)
                    
            if state == '0' and perm_off:
                hp.set_led(False)
            elif state == '1' and perm_on:
                hp.set_led(True)
            else:
                pass
        except ValueError:
            pass
    return render(request, 'devices/led.html', locals())

#only displays the on/off state of a switch
def switch(request):
    return render(request, 'devices/switch.html', locals())
    
def add(request):

    if request.method == 'POST':
        # create a name_form instance and populate it with data from the request:
        name_form = NameForm(request.POST)
        type_form = TypeForm(request.POST)
        # check whether it's valid:
        if name_form.is_valid():
            # process the data in name_form.cleaned_data as required
            given_name = name_form.cleaned_data['device_name']
            #choose type
            type = request.POST['choice_field'] 
            if type == 1:
                device = LED(name = given_name)
                device.save()
            elif type == 2:
                device = Switch(name = given_name)
                device.save()

    # if a GET (or any other method) we'll create a blank name_form
    else:
        name_form = NameForm()
        type_form = TypeForm()

    return render(request, 'devices/add.html', {'name_form': name_form, 'type_form':type_form})

#doesnt handle the case of conflicting names

@csrf_exempt    
@superuser_required
def adduser(request):
    data = request.POST
    uid = data['uid']
    username = data['username']

    #password = str(uuid.uuid4())
    try:
        #change!

        new_user = User.objects.create_user(username, password =  "demo_user")
        print username + ' is added'

        permission = Permission.objects.get(codename='led_view')
        new_user.user_permissions.add(permission)
        new_user.save()
        someperson = Person()
        
        #load keys from db
        f = open(os.path.join(os.path.dirname(os.pardir), "keys.txt"),'r+')
        someperson.keys = f.readline().strip()
        f.write('')
        f.close()

        someperson.uid = uid
        someperson.user = new_user
        someperson.save()
    except IntegrityError:
        #send a msg back to phone
        pass
        
    logout(request)   
    return render(request, 'devices/adduser.html', locals())

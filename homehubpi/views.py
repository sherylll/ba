# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import LED, Person
from django.contrib.auth.models import User, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.middleware.csrf import get_token
from .forms import *

from AESMAC import decrypt_final
import os
import uuid
# Create your views here.

#keys = ['Bar12345Bar12345','abcdef2345678901','2345678901abcdef','passphrase']

def get_keys(uid):
    users = User.objects.all()
    print users
    uid_and_keys = ""
    
    for u in users:
        #print u.person.uid, uid
        if u.person.uid == uid:
            uid_and_keys = u.person.keys.split(',')
            break
    print uid_and_keys
    return uid_and_keys[1:]

sessionID = 'sessionID'

def auth_from_url(authString, request):

    uid = authString[:8]
    login_info = authString[8:]    
    username = request.user.username
    #uid = request.user.person.uid
    
    #no need to encrypt nodeid? diff nodeid & uid? append uid before cred as url?
    keys = get_keys(uid)
    #parse login info
    user_object = None
    if not username and login_info != '':
        #keys is an array
        login_info = decrypt_final(keys, str(login_info), sessionID)
        #not a good idea to seperate with comma...
        #print login_info
        [u, p] = login_info.split(',')
        print "DEBUGGING...\n"
        print u, p
        user_object = authenticate(username = u, password = p)
        username = user_object.username
        if username is not None:
            login(request, user_object)
    return user_object
    
def index(request):
    #sessionID = request.session.session_key
    
    #if not logged in
    if not request.user.has_perm('devices.led_view'):
        path = request.path
        offset = path.find('devices') + 8
        authString = path[offset:]
        
        username = auth_from_url(authString, request).username
    else:
        username = request.user.username
    #for display
    devices = LED.objects.all()
    state = LED().read_led()
    
    response = render(request, 'index.html', locals())
    response['sessionID'] = 'thisIsSessionID'
    return response

def led(request):    
    if not request.user.has_perm('devices.led_view'):
        return redirect('/login/')
   
    if request.method == 'GET':
        state = request.path[-1]
        #print request.user.username
        perm_on = request.user.has_perm('devices.led_on')
        perm_off = request.user.has_perm('devices.led_off')
        print request.user
        
        # Check if the led state is 0 (off) or 1 (on) and set the LED accordingly.
        if state == '0' and perm_off:
            LED().set_led(False)
        elif state == '1' and perm_on:
            LED().set_led(True)
        else:
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
def adduser(request):
    
    #new_uid = request.path[path.find('adduser') + 7:]
    #print new_uid
    data = request.POST
    #print get_token(request)
    name_uid = ""
    for name_uid, uid_authString in data.items():
        if not request.user:
            if not auth_from_url(uid_authString, request).is_superuser:
                #send back some response
                return render(request, 'devices/adduser.html', locals())
    
        #stores keys in add.py file 
        #password = str(uuid.uuid4())
        try:
            name_uid = name_uid.split(',')
            new_user = User.objects.create_user(name_uid[0], password =  "demo_user")     
            print name_uid[0] + ' is added'

            permission = Permission.objects.get(codename='led_view')
            new_user.user_permissions.add(permission)
            new_user.save()
            someperson = Person()
            
            #load keys from db
            f = open(os.path.join(os.path.dirname(os.pardir), "keys.txt"),'r+')
            someperson.keys = f.readline().strip()
            f.write('')
            f.close()
            ###########retrieve from post
            someperson.uid = name_uid[1]
            someperson.user = new_user
            someperson.save()
        except IntegrityError:
            #send a msg back to phone
            pass
            
        logout(request)   
    return render(request, 'devices/adduser.html', locals())

def delete(request):
    return
    
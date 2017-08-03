from django.http import HttpResponse
from devices.models import Publisher,  LED, Person 
from django.core.exceptions import ObjectDoesNotExist
from random import randint,seed, random
from django.contrib.auth.models import User, Permission
from devices.AESMAC import decrypt_final
from django.contrib.auth import authenticate

def publisher(request):
    val =str(randint(1, 1000))
    response = HttpResponse()
    #request.session['sessionID'] = sessionID

    try:
        p = Publisher.objects.get(name="publisher")
        p.sessionID = val
        
        p.save()
    except ObjectDoesNotExist:
        p = Publisher.objects.create(name="publisher",sessionID = val)
        p.save()
    response.set_cookie('sessionID',  val)
    return response
    
###########encryption functions##############

def get_keys(name):
    users = User.objects.all()
    uid_and_keys = []
    for u in users:
        if u.username == name:
            uid_and_keys = u.person.keys.split(',')
            break
    return uid_and_keys
 
def auth_from_url(encrypted_str):

    #username is between the beginning and the next /
    offset = encrypted_str.index("/")
    username = encrypted_str[:offset]
    print username 
    
    data = encrypted_str[offset+1:]    
    
    keys = get_keys(username)
    uid = keys[0]
    keys = keys[1:]
    user_object = None
    #if no keys found return empty user object
    if  len(keys) == 0:
        return user_object
   
    if data != '' :

        sessionID = Publisher.objects.get(name = 'publisher').sessionID
        print data
        real_url = decrypt_final(keys, str(data), sessionID)
        print real_url
        
        """real path: name/led/1/x /password
            encrypted: ???????
            decrypted: led/1/x, username, password
        """
        [useful_url, p] = real_url.split(',')

        user_object = authenticate(username = username, password = p)

        username = user_object.username
        """another step: check url
        """
    return useful_url, user_object
    
#####################   

def rest_set(request):    
   
    if request.method == 'GET':        
        username = None
        #path should be /rest/name/led/1/x
        offset = request.path.find('rest')+5
        encrypted_str = request.path[offset:]

        real_url, user_object = auth_from_url(encrypted_str)
        
        #FIND USER OBJECT
        perm_on = user_object.has_perm('devices.led_on')
        perm_off = user_object.has_perm('devices.led_off') 
        
        print "has led_on permission? " ,perm_on
        print "has led_off permission?", perm_off
        
        #real_url: led/1/x
        state = real_url[-1]
        hotplate_nr = real_url[-3]

        try:
            if not int(hotplate_nr) in range(10):
                pass
            hotplate_name = 'Hotplate '+ hotplate_nr
            hp = LED.objects.get(name = hotplate_name)

            if state == 'x' :
                #change status
                if hp.read_led() and perm_off:
              
                    hp.set_led(False)
                elif perm_on:
                    hp.set_led(True)

        except ValueError:
            pass
        
    return HttpResponse(status=201)
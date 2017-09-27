#main thread in reader mode, if detects superuser, change to client & wait for any input, 
#after input/timeout go back to reader mode

import ndef
import nfc
import nfc.snep
import time
import threading
import uuid
from test_server import snep_server
from binascii import hexlify
from django.core.exceptions import ObjectDoesNotExist
import django
from homehubpi import settings

import RPi.GPIO as GPIO
import time
import sys

#button
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'homehubpi.settings'
django.setup()
from devices.models import LED
from django.contrib.auth.models import User
from devices.models import Person
import signal

flag = True 

uid_list = []
#get uids
#put into function
users = User.objects.all()
for u in users:
    try:
        uid = u.person.uid
    except ObjectDoesNotExist:
        person = Person(user=u)
        uid = person.uid
    if u.has_perm('devices.nfc_feat'):
        if u.is_superuser:
            uid_list.insert(0, uid)
        else:
            uid_list.append(uid)
    
print uid_list
    
"""
cant get updates about change of permissions/adding users
"""
clf= nfc.ContactlessFrontend('tty:AMA0:pn532')
uid = ''
    
def test():
    while flag:
        print "..."
        time.sleep(0.2)
    return 

def read_uid():
    global flag, clf, uid
    while flag:        
        print "thread reader  is running"
        try:
            after2s = lambda: time.time() - started > 1.5
            started = time.time()
            tag = clf.connect(rdwr={'on-connect': lambda tag: False}, terminate = after2s)
            
            uid = hexlify(tag.identifier)
            print uid
            if uid == uid_list[0]: 
                time.sleep(5)
            
        except TypeError:
            uid = ''                  
        except AttributeError:
            uid = ''
            #time.sleep(0.5)
            #print "..."
        except IOError:
            print "reconnect! (adduser)"
            flag = False        
    clf.close()
    return 
    
def add_user():
    global flag, clf,uid
    while flag:       
        #print "thread a  is running"
        try:
            if uid == uid_list[0]: 
                snep_server(clf,4)
                          
        except AttributeError:
            print "attr err (adduser)"
        except TypeError:
            print "type err (adduser)"
        except IOError:
            print "reconnect! (adduser)"
            flag = False
    clf.close()
    return 
    
def button_pressed():
    #return False when pressed   
    global flag, uid
    while flag:        
        #print "thread b  is running"
        try:
            if not GPIO.input(17):
                led0 = LED.objects.get(name =  'Hotplate 0')
                print "button pressed"
                if not led0.nfc_enabled:
                    led0.toggle_led()
                else:
                    #set timeout
                    print "the user detection feature is enabled for this button"
                    if uid in uid_list:
                        print "you are authorized to turn on this button"
                        led0.toggle_led()
                    else:
                        print "wait for authorization"
            else:
                pass
            time.sleep(0.2)
        except AttributeError:
            pass
        except IOError:
            print "reconnect!(button)"
            flag = False 

    clf.close()
    return 
    
def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    global flag, clf
    flag = False
    clf.close()
    sys.exit(0)     

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    #tag = clf.connect(rdwr={'on-connect': lambda tag: False})
    t2 = threading.Thread(target = button_pressed)   
    #t2 = threading.Thread(target = test)
    t1 = threading.Thread(target = add_user)
    t3 = threading.Thread(target = read_uid)

    t3.start()
    t2.start()
    #time.sleep(1)
    t1.start()
    while True:
        time.sleep(1)
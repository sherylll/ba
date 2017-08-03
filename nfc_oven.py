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

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

import os

uid_list = []

os.environ['DJANGO_SETTINGS_MODULE'] = 'homehubpi.settings'
django.setup()
from devices.models import LED
from django.contrib.auth.models import User
from devices.models import Person

#get uids
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
if __name__ == "__main__":
    clf = nfc.ContactlessFrontend('tty:AMA0:pn532')
    tag = clf.connect(rdwr={'on-connect': lambda tag: False})
    #maybe change it to something else
    led = LED.objects.get(name =  'Hotplate 0')

    try:
        flag = False
        while True:
            try:
                tag = clf.connect(rdwr={'on-connect': lambda tag: False})
                # use uid as name
                uid = hexlify(tag.identifier)
                print uid
                
                
                if uid in uid_list:
                    if uid == uid_list[0] and snep_server(clf, 3):
                        pass
                    
                    #time.sleep(2)
                    input_state = GPIO.input(17)
                    if input_state == False:
                        #time.sleep(5)
                        if led.read_led():
                            led.set_led(False)
                        else:
                            led.set_led(True)
                        
                time.sleep(1)
            

            except KeyboardInterrupt:
                break

    finally:
		clf.close()
        
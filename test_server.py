import nfc
import nfc.snep
import time
import django
import os

from devices.AESMAC import decrypt_final, key_parser
from django.db import IntegrityError
successful_recvd = False
my_snep_server = None
uid = ''
os.environ["DJANGO_SETTINGS_MODULE"] = 'homehubpi.settings'
django.setup()

from django.contrib.auth.models import User, Permission
from devices.models import Person
class DefaultSnepServer(nfc.snep.SnepServer):
    def __init__(self, llc):
        nfc.snep.SnepServer.__init__(self, llc, "urn:nfc:sn:snep")

    def put(self, ndef_message):
        global successful_recvd
        print "client has put an NDEF message"

        #keys = nodeid,datakey,staticiv,ivkey,passphrase
        keys = nfc.ndef.TextRecord(ndef_message.pop()).text
        #print keys
        helloMsg = nfc.ndef.TextRecord(ndef_message.pop()).text
        uid, keySet = key_parser(keys)
        #print uid, keySet
        if helloMsg[0:3] == "add":
            try:
                username = helloMsg[4:]
                new_user = User.objects.create_user(username, password =  "demo_user")
                print username + ' is added'

                permission = Permission.objects.get(codename='led_view')
                new_user.user_permissions.add(permission)
                
                permission = Permission.objects.get(codename='led_off')
                new_user.user_permissions.add(permission)
                
                new_user.save()
                someperson = Person()
                someperson.keys = keys
                someperson.uid = keys[:keys.index(",")]
                someperson.user = new_user
                someperson.save()
            except IntegrityError:
                #send a msg back to phone
                pass
                successful_recvd = True
            return nfc.snep.Success
        
        elif  decrypt_final(keySet, helloMsg, "sessionID")== "hello":
            #unnecessary
            f = open('keys.txt', 'w')
            f.write(keys+"\n")
            f.close()            
            print "hello message verified"
            successful_recvd = True
                       
        return nfc.snep.Success

def startup(llc):
    global my_snep_server
    my_snep_server = DefaultSnepServer(llc)
    return llc

def connected(llc):
    my_snep_server.start()
    return True

def snep_server(clf, sec):
    after3s = lambda: time.time() - started > sec
    started = time.time()
    clf.connect(llcp={'on-startup': startup, 'on-connect': connected}, terminate=after3s)
    global successful_recvd
    return successful_recvd

if __name__ == "__main__":
    #this loop deals with the unstable connection
	#while not successful_recvd:
	clf = nfc.ContactlessFrontend('tty:AMA0:pn532')
	try: 
		clf.connect(llcp={'on-startup': startup, 'on-connect': connected})
		print successful_recvd
	except KeyboardInterrupt, IOError:
		pass
	finally:
		clf.close()
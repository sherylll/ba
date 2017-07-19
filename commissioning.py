import ndef

import nfc

import nfc.snep

import time

import threading

from test_server import *
import uuid
from binascii import hexlify

from subprocess import Popen

#password and passphrase
#just in case _ causes any problem...
mm = str(uuid.uuid4())


#ba_uid = bytearray.fromhex('01020304')



#Only after on_connect returns, the llc can start running the symmetry loop (the LLCP heartbeat) with the remote peer 

#and generally receive and dispatch protocol and service data units.

def on_connect_client(llc):    

    threading.Thread(target=llc.run).start(); 



def snep_client(clf):
    global mm, pp    

    llc = clf.connect(llcp={'on-connect': on_connect_client})

    snep = nfc.snep.SnepClient(llc)

	#raspberry is the password, REPLACE WITH RANDOM GEN. PASSWORD

    #send hash key too

    openMessage = [ndef.Record('application/vnd.test.com.openapp'), ndef.TextRecord(mm)]

    try:

        #catches SnepError

        snep.put_records(openMessage, 5.0)

    except:

        pass


status = 'starting'    

if __name__ == "__main__":

    clf = nfc.ContactlessFrontend('tty:AMA0:pn532')

    try:
        while status != 'successful':
            print 'commissioning process is ' + status
            tag = clf.connect(rdwr={'on-connect': lambda tag: False})
            # use uid as name

            uid = hexlify(tag.identifier)

            snep_client(clf)

            #time.sleep(5)
            #create an empty file
            #open('keys.txt', 'w').close()
            if not snep_server(clf, 10):
                print "aborting..."
                status = "aborted"
                break

            #decrypt the hello msg, make sure the user has got the correct key

            #python manage.py createadmin name example@example.com raspberry
            Popen(['python','manage.py','createadmin', 'pi', 'example@example.com', mm, uid])
            #finish the commissioning process
            status = 'successful'
            f = open('user_info.txt', 'w')
            f.write('pi'+' '+uid+' '+'\n')
            f.close()
            #start server
        if status == 'successful':
            Popen(['python','manage.py','runserver', '134.130.223.129:8080'])

    except KeyboardInterrupt:
        pass
        status = 'errored'

    finally:
        clf.close()
        print 'commissioning process is '  + status
import nfc
import nfc.snep
import time
from AESMAC import decrypt_final, key_parser

successful_recvd = False
my_snep_server = None
uid = ''

class DefaultSnepServer(nfc.snep.SnepServer):
    def __init__(self, llc):
        nfc.snep.SnepServer.__init__(self, llc, "urn:nfc:sn:snep")

    def put(self, ndef_message):
        global successful_recvd
        print "client has put an NDEF message"

        #keys = nodeid,datakey,staticiv,ivkey,passphrase
        keys = nfc.ndef.TextRecord(ndef_message.pop()).text
        helloMsg = nfc.ndef.TextRecord(ndef_message.pop()).text
        #keys = '01020304,Bar12345Bar12345,abcdef2345678901,2345678901abcdef,mypassphrase'
        uid, keySet = key_parser(keys)

        #use key set to decrypt 
        print keySet
        if decrypt_final(keySet, helloMsg, "sessionID") == "hello":
            #TODO: if exist r, else a 
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
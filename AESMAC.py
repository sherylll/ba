from base64 import b64encode, b64decode
from M2Crypto.EVP import Cipher
import hmac
import hashlib
import sys

__all__ = ['encryptor', 'decryptor']

ENC=1
DEC=0

def key_parser(data):
    data = data.split(',')
    #data[0] is uid
    return data[0],[data[1], data[2], data[3], data[4]]

def build_cipher(key, iv, op=ENC):
    """"""""
    return Cipher(alg='aes_128_cbc', key=key, iv=iv, op=op, padding = True)

def encryptor(key, iv=None):
    """"""
    # Decode the key and iv
    key = b64decode(key)
    if iv is None:
        iv = '\0' * 16
    else:
        iv = b64decode(iv)
   
    #Return the encryption function
    def encrypt(data):
        cipher = build_cipher(key, iv, ENC)
        v = cipher.update(data)
        v = v + cipher.final()
        del cipher
        v = b64encode(v)
        return v
    return encrypt

def decryptor(key, iv=None):
    """"""
    # Decode the key and iv
    key = b64decode(key)
    if iv is None:
        iv = '\0' * 16
    else:
        iv = b64decode(iv)

   # Return the decryption function
    def decrypt(data):
        data = b64decode(data)
        cipher = build_cipher(key, iv, DEC)
        v = cipher.update(data)
        v = v + cipher.final()
        del cipher
        return v
    return decrypt

def encrypt_final(keys, nodeid, iv, data, sessionID):
    datakey = keys[0]	
    staticiv = keys[1]
    ivkey = keys[2]
    passphrase = keys[3]

    fullmessage = ','.join([nodeid, iv, data, sessionID])
    mac = hmac.new(passphrase, msg=fullmessage, digestmod=hashlib.sha1).hexdigest()
    
    iv_encryptor = encryptor(b64encode(ivkey), b64encode(staticiv))
    encrypted_iv = iv_encryptor(iv)
    
    nodeid_encryptor = encryptor(b64encode(datakey), b64encode(iv))
    encrypted_nodeid = nodeid_encryptor(nodeid)
    
    data_encryptor = encryptor(b64encode(datakey), b64encode(iv))
    encrypted_data = data_encryptor(data)    

    return encrypted_iv + ',' + encrypted_nodeid + ','  + encrypted_data + ',' + mac
    

#returns data
def decrypt_final(keys, data, sessionID):
	#keys passed as array, data as string...
	datakey = keys[0]	
	staticiv = keys[1]
	ivkey = keys[2]
	passphrase = keys[3]

	data = data.split(",")
	encrypted_iv = data[0]
	encrypted_nodeid = data[1]
	encrypted_data = data[2]
	recvd_hmac = data[3]

	iv_decryptor = decryptor(b64encode(ivkey), b64encode(staticiv))
	iv = iv_decryptor(encrypted_iv)
	#print iv

	nodeid_decryptor = decryptor(b64encode(datakey), b64encode(iv))
	nodeid = nodeid_decryptor(encrypted_nodeid)

	data_decryptor = decryptor(b64encode(datakey), b64encode(iv))
	data = data_decryptor(encrypted_data)

	fullmessage = ','.join([nodeid, iv, data, sessionID])
	computed_mac = hmac.new(str(passphrase), msg=str(fullmessage), digestmod=hashlib.sha1).hexdigest()
	#print fullmessage    
	#print recvd_hmac +'\n' +computed_mac
	if recvd_hmac == computed_mac:
		return data
	else:
		return "lol"
    

if __name__ == "__main__":
	nfc_data = '01020304,Bar12345Bar12345,abcdef2345678901,2345678901abcdef,mypassphrase'
	uid, keys = key_parser(nfc_data)
	iv = 'thisisNotranDom.' #different for each message sent
	nodeid = '01020304'
	data = 'pi,raspberry'
	data = str(sys.argv[1])
	#print data
	sessionID = 'sessionID'

	sent_data = encrypt_final(keys, nodeid, iv, data, sessionID)
	sent_data = '/CuwV/6OPG9jmpWnp8CttQZ6bDpglGj7+xREqfGa3/Q=,1U+E1wQoz1Umo135vvk3Hg==,pQT2VTfRSMuG3wLasVUuRA==,eb983181dddb79e5d24521d8c88c487e3e75dee2'
	print decrypt_final(keys, sent_data, sessionID)
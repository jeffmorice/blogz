import hashlib
import random
import string

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
    # encodes the password as a set of bytes, required by sha256
    ### p_encoded = str.encode(password)
    # creates hash object from encoded password
    ### hash_object = hashlib.sha256(p_encoded)
    # gets hash string from hash object
    ### hash_str = hash_object.hexdigest()

    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash, salt)

def check_pw_hash(password, hash):
    salt = hash.split(',')[1]
    if make_pw_hash(password, salt) == hash:
        return True

    return False

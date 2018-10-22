import hashlib

def make_pw_hash(password):
    # encodes the password as a set of bytes, required by sha256
    ### p_encoded = str.encode(password)
    # creates hash object from encoded password
    ### hash_object = hashlib.sha256(p_encoded)
    # gets hash string from hash object
    ### hash_str = hash_object.hexdigest()

    return hashlib.sha256(str.encode(password)).hexdigest()

def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True
        
    return False

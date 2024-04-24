from passlib.context import CryptContext

crypt_context = CryptContext(['bcrypt'])


def hash_password(password):
    return crypt_context.hash(password)

def verify_password(password, hash):
    return crypt_context.verify(password, hash)




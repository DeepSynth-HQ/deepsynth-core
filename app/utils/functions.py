import hashlib
import uuid


def ref_generator(input_string):
    hash_object = hashlib.sha256(input_string.encode())
    full_hash = hash_object.hexdigest()
    short_hash = full_hash[:6]
    return short_hash


def generate_uuid():
    return str(uuid.uuid4())


def generate_referral_code():
    import random
    import string

    chars = "".join(c for c in string.ascii_letters + string.digits if c not in "01OIL")
    return "".join(random.choices(chars, k=8))


if __name__ == "__main__":
    for _ in range(100):
        print(generate_referral_code())

from argon2 import PasswordHasher


def split_email(email):
    """Splits email in username and domain part."""
    username, domain = email.split('@')
    return username, domain


def gen_password_hash(password):
    """Helper function to generate ARGON2ID-hash."""
    hash_scheme = "{ARGON2ID}"
    hash_password = PasswordHasher().hash(password)
    complete_hash = f"{hash_scheme}{hash_password}"
    return complete_hash

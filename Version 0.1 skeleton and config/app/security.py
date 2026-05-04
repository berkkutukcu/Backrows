import secrets

import bcrypt

_BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:72], hashed.encode("utf-8"))
    except ValueError:
        return False


def create_qr_token() -> str:
    return secrets.token_urlsafe(24)


def create_verification_code() -> str:
    return f"{secrets.randbelow(10000):04d}"

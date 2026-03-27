import bcrypt
from passlib.context import CryptContext

# Use pbkdf2_sha256 as the default scheme. Keep compatibility with legacy
# bcrypt hashes that may already exist in the database.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def get_hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False

    # Existing users may still have legacy bcrypt hashes.
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    return pwd_context.verify(plain_password, hashed_password)

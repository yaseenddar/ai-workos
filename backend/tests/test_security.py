from app.core.security import hash_password, verify_password


def test_password_hashing():
    password = "MySecretPassword123"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password_hash.startswith("$argon2id$")


def test_password_verification():
    password = "MySecretPassword123"

    password_hash = hash_password(password)

    assert verify_password(password, password_hash)


def test_wrong_password_fails():
    password_hash = hash_password("MySecretPassword123")

    assert not verify_password(
        "WrongPassword",
        password_hash,
    )


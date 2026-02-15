from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

def register_user(username, password):
    db = get_db()
    cursor = db.cursor()

    hashed_pw = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO voters (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )
        db.commit()
        return True
    except:
        return False
    finally:
        db.close()


def login_user(username, password):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM voters WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    db.close()

    if user and check_password_hash(user["password"], password):
        return user
    return None
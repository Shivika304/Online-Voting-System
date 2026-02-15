from database import get_db

def cast_vote(voter_id, candidate_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT has_voted FROM voters WHERE id = ?",
        (voter_id,)
    )
    voted = cursor.fetchone()["has_voted"]

    if voted:
        return False

    cursor.execute(
        "INSERT INTO votes (voter_id, candidate_id) VALUES (?, ?)",
        (voter_id, candidate_id)
    )

    cursor.execute(
        "UPDATE voters SET has_voted = 1 WHERE id = ?",
        (voter_id,)
    )

    db.commit()
    db.close()
    return True
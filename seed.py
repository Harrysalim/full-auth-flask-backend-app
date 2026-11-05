from faker import Faker

from app import create_app
from extensions import db
from models import Note, User

fake = Faker()

def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        Note.query.delete()
        User.query.delete()

        users = []
        for username in ("alice", "bob", "charlie"):
            user = User(username=username)
            user.set_password("password123")
            db.session.add(user)
            users.append(user)

        db.session.flush()

        for user in users:
            for _ in range(5):
                db.session.add(
                    Note(
                        title=fake.sentence(nb_words=4).rstrip("."),
                        content=fake.paragraph(nb_sentences=3),
                        user_id=user.id,
                    )
                )
        
        db.session.commit()
        print("Database seeded: 3 users and 15 notes.")
        print("Demo password for each user: password123")


if __name__ == "__main__":
    seed_database()
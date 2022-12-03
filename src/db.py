import datetime
import hashlib
import os

import bcrypt
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

association_table_journals_tags = db.Table("association_s", db.Model.metadata,
                                           db.Column("entry_id", db.Integer,
                                                     db.ForeignKey("entry.id")),
                                           db.Column("tag_id", db.Integer,
                                                     db.ForeignKey("tag.id"))
                                           )

# association_table_journals_emotions = db.Table("association_e", db.Model.metadata,
#                                            db.Column("entry_id", db.Integer,
#                                                      db.ForeignKey("entry.id")),
#                                            db.Column("emotion_id", db.Integer,
#                                                      db.ForeignKey("emotion.id"))
#                                            )

class User(db.Model):
    """
    User model
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    # User information
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)

    # Entry information
    entries = db.relationship("Entry", cascade="delete")

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        """
        Initializes a User object
        """
        self.email = kwargs.get("email")
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.renew_session()

    def get_user_entries(self):
        return {
            "entries": [e.serialize() for e in self.entries]
        }

    def _urlsafe_base_64(self):
        """
        Randomly generates hashed tokens (used for session/update tokens)
        """
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def renew_session(self):
        """
        Renews the sessions, i.e.
        1. Creates a new session token
        2. Sets the expiration time of the session
        3. Creates a new update token
        """
        self.session_token = self._urlsafe_base_64()
        # Change expiration time accordingly
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=30)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        """
        Verifies the password of a user
        """
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    def verify_session_token(self, session_token):
        """
        Verifies the session token of a user
        """
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        """
        Verifies the update token of a user
        """
        return update_token == self.update_token


class Entry(db.Model):
    '''
    Database representing a Entry of the Journal
    Contains a title, content, emotion, date, and a link to the association table of entries to tags  
    '''
    __tablename__ = "entry"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    # Should be "" when empty
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    emotion = db.Column(db.String, nullable=False)
    
    date = db.Column(db.String, nullable=True)

    # entry_emotions = db.relationship(
    #     "Emotion", secondary=association_table_journals_emotions, back_populates='emotion_entries'
    # )

    entry_tags = db.relationship(
        "Tag", secondary=association_table_journals_tags, back_populates='tag_entries')

    def __init__(self, **kwargs) -> None:
        self.title = kwargs["title"]
        self.content = kwargs["content"]
        self.user_id = kwargs["user"]
        self.emotion = kwargs["emotion"]
        self.date = datetime.datetime.now()

    def info(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "emotion": self.emotion,
            "date": self.date
        }

    def serialize(self):
        i = self.info()
        i.update({"tags": [c.info() for c in self.entry_tags]})
        return i


class Tag(db.Model):
    '''
    Database representing a Tag
    Contains a name, color, and a link to the association table of entries to tags
    '''
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)

    tag_entries = db.relationship(
        "Entry", secondary=association_table_journals_tags, back_populates='entry_tags')

    def __init__(self, **kwargs) -> None:
        self.name = kwargs["name"]
        self.color = kwargs["color"]

    def info(self):
        return {
            "name": self.name,
            "color": self.color
        }

    def serialize(self):
        i = self.info()
        i.update({"entries": [c.info() for c in self.tag_entries]})
        return i


# class Emotion(db.Model):
#     '''
#     Database representing a Emotion
#     Contains a name, color, and a link to the association table of entries to emotions
#     '''
#     __tablename__ = "emotion"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String, nullable=False)
#     color = db.Column(db.String, nullable=False)

#     emotion_entries = db.relationship(
#         "Entry", secondary=association_table_journals_emotions, back_populates='entry_emotions')

#     def __init__(self, **kwargs) -> None:
#         self.name = kwargs["name"]
#         self.color = kwargs["color"]

#     def info(self):
#         return {
#             "name": self.name,
#             "color": self.color
#         }

#     def serialize(self):
#         i = self.info()
#         i.update({"entries": [c.info() for c in self.emotion_entries]})
#         return i

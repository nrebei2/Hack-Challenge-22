import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_journals_tags = db.Table("association_s", db.Model.metadata,
                                           db.Column("entry_id", db.Integer,
                                                     db.ForeignKey("entry.id")),
                                           db.Column("tag_id", db.Integer,
                                                     db.ForeignKey("tag.id"))
                                           )

association_table_journals_emotions = db.Table("association_e", db.Model.metadata,
                                           db.Column("entry_id", db.Integer,
                                                     db.ForeignKey("entry.id")),
                                           db.Column("emotion_id", db.Integer,
                                                     db.ForeignKey("emotion.id"))
                                           )


class Entry(db.Model):
    '''
    Database representing a Entry of the Journal
    Contains a title, content, emotion, date, and a link to the association table of entries to tags  
    '''
    __tablename__ = "entry"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=True)
    
    date = db.Column(db.String, nullable=True)

    entry_emotions = db.relationship(
        "Emotion", secondary=association_table_journals_emotions, back_populates='emotion_entries'
    )
    entry_tags = db.relationship(
        "Tag", secondary=association_table_journals_tags, back_populates='tag_entries')

    def __init__(self, **kwargs) -> None:
        self.title = kwargs["title"]
        self.content = kwargs["content"]
        self.date = datetime.datetime.now()

    def info(self):
        return {
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


class Emotion(db.Model):
    '''
    Database representing a Emotion
    Contains a name, color, and a link to the association table of entries to emotions
    '''
    __tablename__ = "emotion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)

    emotion_entries = db.relationship(
        "Entry", secondary=association_table_journals_emotions, back_populates='entry_emotions')

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
        i.update({"entries": [c.info() for c in self.emotion_entries]})
        return i

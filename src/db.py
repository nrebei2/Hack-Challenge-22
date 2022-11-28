import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_journals_tags = db.Table("association_s", db.Model.metadata,
                                           db.Column("entry_id", db.Integer,
                                                     db.ForeignKey("entry.id")),
                                           db.Column("tag_id", db.Integer,
                                                     db.ForeignKey("tag.id"))
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
    emotion = db.Column(db.Float, nullable=False)
    date = db.Column(db.String, nullable=True)

    entry_tags = db.relationship(
        "Tag", secondary=association_table_journals_tags, back_populates='tag_entries')

    def __init__(self, **kwargs) -> None:
        self.title = kwargs["title"]
        self.content = kwargs["content"]
        self.emotion = kwargs["emotion"]
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

    tag_entries = db.relationship(
        "Entry", secondary=association_table_journals_tags, back_populates='entry_tags')

    def __init__(self) -> None:
        super().__init__()

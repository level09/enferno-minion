from extensions import db


class Apartment(db.Document):
    title = db.StringField()
    url = db.StringField()
    price = db.IntField()

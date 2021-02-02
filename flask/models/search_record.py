from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class SearchRecord(db.Model):
    __tablename__ = 'search_records'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(80))
    category_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    sex = db.Column(db.String(24))
    distance = db.Column(db.String(24))
    hits = db.Column(db.Integer)
    country = db.Column(db.String(24))
    city = db.Column(db.String(24))
    created_at = db.Column(db.String(24))
    updated_at = db.Column(db.String(24))  

    def __repr__(self):
        return '<Query %r>' % self.query 
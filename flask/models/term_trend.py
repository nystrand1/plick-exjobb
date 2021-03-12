from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class TermTrend(db.Model):
    __table_args__ = {"schema":"search_records"}
    __tablename__ = 'term_trends'
    id = db.Column(db.Integer, autoincrement=True)
    query = db.Column(db.String(80), primary_key=True)
    model_short = db.Column(db.ARRAY(db.Float))
    model_mid = db.Column(db.ARRAY(db.Float))
    model_long = db.Column(db.ARRAY(db.Float))
    similar_queries = db.Column(db.ARRAY(db.String))
    created_at = db.Column(db.String(100))
    updated_at = db.Column(db.String(100))  

    def __repr__(self):
        return '<Query %r>' % self.query 

    def create(self):
        db.create_all()
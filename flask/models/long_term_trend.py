from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class LongTermTrend(db.Model):
    __table_args__ = {"schema":"search_records"}
    __tablename__ = 'long_term_trends'
    id = db.Column(db.Integer, autoincrement=True)
    query = db.Column(db.String(80), primary_key=True)
    k_value = db.Column(db.Float(48))
    interval = db.Column(db.String(80))
    created_at = db.Column(db.String(100))
    updated_at = db.Column(db.String(100))  

    def __repr__(self):
        return '<Query %r>' % self.query 

    def create(self):
        db.create_all()
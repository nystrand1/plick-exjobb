from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class TermTrend(db.Model):
    __table_args__ = {"schema":"plick"}
    __tablename__ = 'term_trends'
    query = db.Column(db.String(80), primary_key=True)
    similar_queries = db.Column(db.ARRAY(db.String))
    model_short = db.Column(db.ARRAY(db.Float))
    model_mid = db.Column(db.ARRAY(db.Float))
    model_long = db.Column(db.ARRAY(db.Float))
    model_sarima = db.Column(db.String(128))    
    model_lstm = db.Column(db.String(128))
    time_series_min = db.Column(db.JSON)
    time_series_hour = db.Column(db.JSON)
    time_series_day = db.Column(db.JSON)
    time_series_week = db.Column(db.JSON)
    time_series_month = db.Column(db.JSON)
    created_at = db.Column(db.String(100))
    updated_at = db.Column(db.String(100))  

    def __repr__(self):
        return '<Query %r>' % self.query 

    def create(self):
        db.create_all()
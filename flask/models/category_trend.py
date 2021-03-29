from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class CategoryTrend(db.Model):
    __table_args__ = {"schema":"plick"}
    __tablename__ = 'category_trends'
    id = db.Column(db.Integer, primary_key=True)
    category_ids = db.Column(db.ARRAY(db.Integer))
    category_names = db.Column(db.ARRAY(db.Text))
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
        return '<Category %r>' % self.category 

    def create(self):
        db.create_all()
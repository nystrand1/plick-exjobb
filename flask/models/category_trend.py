from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class CategoryTrend(db.Model):
    __table_args__ = {"schema":"plick"}
    __tablename__ = 'category_trends'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(80))
    model_short = db.Column(db.ARRAY(db.Float))
    model_mid = db.Column(db.ARRAY(db.Float))
    model_long = db.Column(db.ARRAY(db.Float))
    future_model = db.Column(db.ARRAY(db.Float))
    model_sarima = db.Column(db.LargeBinary)    
    model_lstm = db.Column(db.LargeBinary)
    model_tcn = db.Column(db.LargeBinary)
    tcn_prediction = db.Column(db.JSON)
    lstm_prediction = db.Column(db.JSON)
    sarima_prediction = db.Column(db.JSON)
    tcn_metrics = db.Column(db.JSON)
    lstm_metrics = db.Column(db.JSON)
    sarima_metrics = db.Column(db.JSON)
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
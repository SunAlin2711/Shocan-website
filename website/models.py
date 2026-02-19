from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta # добавила
import secrets #добавила

class Note(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default = func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id =  db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

#добавила
class ResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)          # безопасный токен ~43 символа
        self.expires_at = datetime.utcnow() + timedelta(hours=1)  # живёт 1 час
# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Shoutbox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    message = db.Column(db.Text)
    timestamp = db.Column(db.String(20))

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20))  # Announcements, General, MM Service
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    username = db.Column(db.String(50))
    date = db.Column(db.String(20))

class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20))  # Buyers, Sellers
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    username = db.Column(db.String(50))
    price = db.Column(db.String(20))
    date = db.Column(db.String(20))

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20))  # Buy, Sell
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    username = db.Column(db.String(50))
    price = db.Column(db.String(20))
    date = db.Column(db.String(20))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_type = db.Column(db.String(20))  # announcement, marketplace, service
    post_id = db.Column(db.Integer)
    username = db.Column(db.String(50))
    content = db.Column(db.Text)
    date = db.Column(db.String(20))

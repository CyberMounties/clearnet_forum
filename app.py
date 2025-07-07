# app.py
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Shoutbox, Announcement, Marketplace, Service, Comment

app = Flask(__name__)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Routes for pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/marketplace')
def marketplace():
    return render_template('marketplace.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/category/<post_type>/<category>')
def category(post_type, category):
    return render_template('category.html', post_type=post_type, category=category)

# API endpoints for dynamic data
@app.route('/api/shoutbox')
def get_shoutbox():
    shoutbox = Shoutbox.query.order_by(Shoutbox.timestamp.desc()).limit(10).all()
    return jsonify([{
        'id': item.id,
        'username': item.username,
        'message': item.message,
        'timestamp': item.timestamp
    } for item in shoutbox])

@app.route('/api/announcements')
def get_announcements():
    announcements = Announcement.query.order_by(Announcement.date.desc()).limit(5).all()
    return jsonify([{
        'id': item.id,
        'category': item.category,
        'title': item.title,
        'content': item.content,
        'username': item.username,
        'date': item.date
    } for item in announcements])

@app.route('/api/marketplace')
def get_marketplace():
    marketplace = Marketplace.query.order_by(Marketplace.date.desc()).limit(10).all()
    return jsonify([{
        'id': item.id,
        'category': item.category,
        'title': item.title,
        'description': item.description,
        'username': item.username,
        'price': item.price,
        'date': item.date
    } for item in marketplace])

@app.route('/api/services')
def get_services():
    services = Service.query.order_by(Service.date.desc()).limit(10).all()
    return jsonify([{
        'id': item.id,
        'category': item.category,
        'title': item.title,
        'description': item.description,
        'username': item.username,
        'price': item.price,
        'date': item.date
    } for item in services])

@app.route('/api/category_counts')
def get_category_counts():
    counts = {
        'announcements': {
            'Announcements': Announcement.query.filter_by(category='Announcements').count(),
            'General': Announcement.query.filter_by(category='General').count(),
            'MM Service': Announcement.query.filter_by(category='MM Service').count()
        },
        'marketplace': {
            'Buyers': Marketplace.query.filter_by(category='Buyers').count(),
            'Sellers': Marketplace.query.filter_by(category='Sellers').count()
        },
        'services': {
            'Buy': Service.query.filter_by(category='Buy').count(),
            'Sell': Service.query.filter_by(category='Sell').count()
        }
    }
    return jsonify(counts)

@app.route('/api/posts/<post_type>/<category>')
def get_posts_by_category(post_type, category):
    if post_type == 'announcements':
        posts = Announcement.query.filter_by(category=category).order_by(Announcement.date.desc()).all()
        return jsonify([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'content': post.content,
            'username': post.username,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='announcement', post_id=post.id).count()
        } for post in posts])
    elif post_type == 'marketplace':
        posts = Marketplace.query.filter_by(category=category).order_by(Marketplace.date.desc()).all()
        return jsonify([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'username': post.username,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='marketplace', post_id=post.id).count()
        } for post in posts])
    elif post_type == 'services':
        posts = Service.query.filter_by(category=category).order_by(Service.date.desc()).all()
        return jsonify([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'username': post.username,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='service', post_id=post.id).count()
        } for post in posts])
    return jsonify([])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

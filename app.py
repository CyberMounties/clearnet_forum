# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Shoutbox, Announcement, Marketplace, Service, Comment
import string, random, os 
from captcha.image import ImageCaptcha


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
@login_required
def search():
    return render_template('search.html')

# CAPTCHA configuration
CAPTCHA_LENGTH = 8
CAPTCHA_CHARS = string.ascii_uppercase + string.digits
image_captcha = ImageCaptcha(fonts=['fonts/DejaVuSans.ttf'], width=200, height=60)


def generate_captcha():
    """Generate an 8-character CAPTCHA and image."""
    code = ''.join(random.choice(CAPTCHA_CHARS) for _ in range(CAPTCHA_LENGTH))
    image_path = os.path.join('static', 'captchas', f'captcha_{code}.png')
    image_captcha.write(code, image_path)
    return code, image_path

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # Generate CAPTCHA for GET request
    if request.method == 'GET':
        captcha_code, captcha_image = generate_captcha()
        session['captcha'] = captcha_code
        session['captcha_image'] = captcha_image
        return render_template('login.html', captcha_image=captcha_image)
    
    # Handle POST request
    username = request.form['username']
    password = request.form['password']
    captcha_input = request.form['captcha'].strip().upper()
    
    # Validate CAPTCHA first
    if captcha_input != session.get('captcha'):
        flash('Invalid CAPTCHA', 'danger')
        # Generate new CAPTCHA for next attempt
        captcha_code, captcha_image = generate_captcha()
        session['captcha'] = captcha_code
        session['captcha_image'] = captcha_image
        return render_template('login.html', captcha_image=captcha_image)
    
    # Validate credentials
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        captcha_image = session.get('captcha_image')
        session.pop('captcha', None)
        session.pop('captcha_image', None)
        if captcha_image:  # Ensure path exists before removing
            try:
                os.remove(captcha_image)
            except OSError as e:
                print(f"Error deleting CAPTCHA image: {e}")
        return redirect(url_for('home'))
    
    flash('Invalid username or password', 'danger')
    # Generate new CAPTCHA for next attempt
    captcha_code, captcha_image = generate_captcha()
    session['captcha'] = captcha_code
    session['captcha_image'] = captcha_image  # Store new image path
    return render_template('login.html', captcha_image=captcha_image)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('register.html')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, avatar='default.jpg')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/category/<post_type>/<category>')
def category(post_type, category):
    page = request.args.get('page', 1, type=int)
    return render_template('category.html', post_type=post_type, category=category, page=page)

@app.route('/post/<post_type>/<int:post_id>')
@login_required
def post_detail(post_type, post_id):
    if post_type == 'announcements':
        post = Announcement.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_type='announcement', post_id=post_id).order_by(Comment.date.desc()).all()
    elif post_type == 'marketplace':
        post = Marketplace.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_type='marketplace', post_id=post_id).order_by(Comment.date.desc()).all()
    elif post_type == 'services':
        post = Service.query.get_or_404(post_id)
        comments = Comment.query.filter_by(post_type='service', post_id=post_id).order_by(Comment.date.desc()).all()
    else:
        return render_template('404.html'), 404
    user = User.query.get_or_404(post.user_id)
    post_count = len(user.announcements) + len(user.marketplace_posts) + len(user.services)
    return render_template('post_detail.html', post=post, post_type=post_type, comments=comments, user=user, post_count=post_count)

@app.route('/profile/<username>')
@login_required
def profile_detail(username):
    user = User.query.filter_by(username=username).first_or_404()
    post_count = len(user.announcements) + len(user.marketplace_posts) + len(user.services)
    posts = []
    for post in user.announcements:
        posts.append({
            'post_type': 'announcements',
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'content': post.content,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='announcement', post_id=post.id).count()
        })
    for post in user.marketplace_posts:
        posts.append({
            'post_type': 'marketplace',
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='marketplace', post_id=post.id).count()
        })
    for post in user.services:
        posts.append({
            'post_type': 'services',
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'price': post.price,
            'date': post.date,
            'comments': Comment.query.filter_by(post_type='service', post_id=post.id).count()
        })
    return render_template('profile_detail.html', user=user, post_count=post_count, posts=posts)

# API endpoints for dynamic data
@app.route('/api/shoutbox')
def get_shoutbox():
    shoutbox = Shoutbox.query.order_by(Shoutbox.timestamp.desc()).limit(10).all()
    return jsonify([{
        'id': item.id,
        'username': item.author.username,
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
        'username': item.author.username,  # Changed from user to author
        'date': item.date
    } for item in announcements])

@app.route('/api/marketplace')
def get_marketplace():
    marketplace = Marketplace.query.order_by(Marketplace.date.desc()).limit(10).all()
    return jsonify([{
        'id': item.id,
        'category': item.category,
        'title': item.title,
        'description': item.description.replace('\n', '<br>'),  # Replace newlines for HTML
        'username': item.author.username,  # Changed from user to author
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
        'username': item.author.username,  # Changed from user to author
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
    page = request.args.get('page', 1, type=int)
    per_page = 10
    if post_type == 'announcements':
        posts = Announcement.query.filter_by(category=category).order_by(Announcement.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'posts': [{
                'id': post.id,
                'category': post.category,
                'title': post.title,
                'content': post.content,
                'username': post.author.username,  # Changed from user to author
                'date': post.date,
                'comments': Comment.query.filter_by(post_type='announcement', post_id=post.id).count()
            } for post in posts.items],
            'total_pages': posts.pages,
            'current_page': posts.page
        })
    elif post_type == 'marketplace':
        posts = Marketplace.query.filter_by(category=category).order_by(Marketplace.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'posts': [{
                'id': post.id,
                'category': post.category,
                'title': post.title,
                'description': post.description.replace('\n', '<br>'),  # Replace newlines for HTML
                'username': post.author.username,  # Changed from user to author
                'price': post.price,
                'date': post.date,
                'comments': Comment.query.filter_by(post_type='marketplace', post_id=post.id).count()
            } for post in posts.items],
            'total_pages': posts.pages,
            'current_page': posts.page
        })
    elif post_type == 'services':
        posts = Service.query.filter_by(category=category).order_by(Service.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'posts': [{
                'id': post.id,
                'category': post.category,
                'title': post.title,
                'description': post.description,
                'username': post.author.username,  # Changed from user to author
                'price': post.price,
                'date': post.date,
                'comments': Comment.query.filter_by(post_type='service', post_id=post.id).count()
            } for post in posts.items],
            'total_pages': posts.pages,
            'current_page': posts.page
        })
    return jsonify({'posts': [], 'total_pages': 0, 'current_page': 1})

@app.route('/api/search', methods=['GET'])
@login_required
def search_posts():
    query = request.args.get('query', '')
    post_type = request.args.get('type', '')
    posts = []
    if post_type == '' or post_type == 'announcements':
        announcements = Announcement.query.filter(
            (Announcement.title.ilike(f'%{query}%')) |
            (Announcement.content.ilike(f'%{query}%'))
        ).all()
        posts.extend([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'content': post.content,
            'username': post.author.username,  # Changed from user to author
            'date': post.date,
            'post_type': 'announcements'
        } for post in announcements])
    if post_type == '' or post_type == 'marketplace':
        marketplace = Marketplace.query.filter(
            (Marketplace.title.ilike(f'%{query}%')) |
            (Marketplace.description.ilike(f'%{query}%'))
        ).all()
        posts.extend([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description.replace('\n', '<br>'),  # Replace newlines for HTML
            'username': post.author.username,  # Changed from user to author
            'price': post.price,
            'date': post.date,
            'post_type': 'marketplace'
        } for post in marketplace])
    if post_type == '' or post_type == 'services':
        services = Service.query.filter(
            (Service.title.ilike(f'%{query}%')) |
            (Service.description.ilike(f'%{query}%'))
        ).all()
        posts.extend([{
            'id': post.id,
            'category': post.category,
            'title': post.title,
            'description': post.description,
            'username': post.author.username,  # Changed from user to author
            'price': post.price,
            'date': post.date,
            'post_type': 'services'
        } for post in services])
    return jsonify(posts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
# populate_db.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User, Shoutbox, Announcement, Marketplace, Service, Comment
from datetime import datetime, timedelta
import random
import logging
from transformers import pipeline

# Configuration variables
NUM_SHOUTBOX_MESSAGES = 20
NUM_POSTS_PER_CATEGORY = 13
NUM_COMMENTS_PER_POST = 2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('populate_db.log')
    ]
)
logger = logging.getLogger(__name__)

# Suppress transformers verbose output
logging.getLogger('transformers').setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt = Bcrypt(app)

# Initialize NLP pipeline
generator = pipeline('text-generation', model='gpt2', device=-1)  # -1 for CPU

def generate_text(prompt, max_tokens, batch_size=1):
    try:
        results = generator(
            [prompt] * batch_size,
            max_new_tokens=max_tokens,
            num_return_sequences=1,
            truncation=True,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        texts = [result[0]['generated_text'].replace(prompt, '').strip() for result in results]
        return texts[0] if batch_size == 1 else texts
    except Exception as e:
        logger.error(f"Error generating text for prompt '{prompt}': {str(e)}")
        return ["Generated text error"] * batch_size

def init_db():
    with app.app_context():
        logger.info("Starting database initialization")
        db.drop_all()
        logger.info("Dropped existing tables")
        db.create_all()
        logger.info("Created new tables")

        # Create 10 user profiles
        users = [
            ('DarkHacker', 'pass123', 'darkhacker.jpg'),
            ('CyberGhost', 'ghost456', 'cyberghost.jpg'),
            ('ShadowV', 'shadow789', 'shadowv.jpg'),
            ('AnonX', 'anon101', 'anonx.jpg'),
            ('N3tRunn3r', 'runner202', 'netrunner.jpg'),
            ('Crypt0King', 'king303', 'cryptoking.jpg'),
            ('ZeroByte', 'zero404', 'zerobyte.jpg'),
            ('HackSavvy', 'savvy505', 'hacksavvy.jpg'),
            ('GhostRider', 'rider606', 'ghostrider.jpg'),
            ('DataViper', 'viper707', 'dataviper.jpg'),
        ]
        for username, password, avatar in users:
            if not User.query.filter_by(username=username).first():
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                user = User(username=username, password=hashed_password, avatar=avatar)
                db.session.add(user)
                logger.info(f"Added user: {username}")
        try:
            db.session.commit()
            logger.info("Committed 10 users to database")
        except Exception as e:
            logger.error(f"Error committing users: {str(e)}")
            db.session.rollback()
            return

        user_ids = [user.id for user in User.query.all()]

        # Generate timestamps (within last 30 days)
        def random_timestamp():
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            seconds_ago = random.randint(0, 59)
            return (datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago, seconds=seconds_ago)).strftime('%Y-%m-%d %H:%M:%S')

        # Prompts for different categories
        announcement_prompts = [
            "Announce new rules for trading compromised RDP credentials: ",
            "Discuss recent trends in dark web data breaches: ",
            "Offer middleman services for secure IAB deals: ",
            "Share tips for safe phishing kit trading: "
        ]
        marketplace_prompts = [
            "Offer fresh SSH keys for sale: ",
            "Seek stolen credit card details for purchase: ",
            "Sell hacked PayPal accounts: ",
            "Look for high-quality botnet access: "
        ]
        service_prompts = [
            "Offer professional DDoS attack services: ",
            "Seek an expert for custom malware development: ",
            "Provide phishing campaign setup services: ",
            "Request SQL injection expertise: "
        ]
        comment_prompts = [
            "Express interest in an IAB deal: ",
            "Ask for details on a cyber-crime service: ",
            "Confirm a successful transaction for stolen data: "
        ]

        # Populate Shoutbox
        logger.info(f"Populating shoutbox with {NUM_SHOUTBOX_MESSAGES} messages")
        for i in range(0, NUM_SHOUTBOX_MESSAGES, 5):  # Batch of 5
            batch_size = min(5, NUM_SHOUTBOX_MESSAGES - i)
            prompt = random.choice([
                "Shout about new IAB marketplace drops: ",
                "Seek cyber-crime services in a shoutbox: ",
                "Announce fresh non-IAB data for sale: "
            ])
            messages = generate_text(prompt, max_tokens=50, batch_size=batch_size)
            for j, message in enumerate(messages):
                shout = Shoutbox(
                    user_id=random.choice(user_ids),
                    message=message[:50],
                    timestamp=random_timestamp()
                )
                db.session.add(shout)
                logger.info(f"Added shoutbox message {i + j + 1}/{NUM_SHOUTBOX_MESSAGES}: {message[:30]}...")
            try:
                db.session.commit()
                logger.info(f"Committed shoutbox messages {i + 1}-{i + batch_size}")
            except Exception as e:
                logger.error(f"Error committing shoutbox messages: {str(e)}")
                db.session.rollback()
                return

        # Populate Announcements (NUM_POSTS_PER_CATEGORY per category: Announcements, General, MM Service)
        categories = ['Announcements', 'General', 'MM Service']
        for category in categories:
            logger.info(f"Populating {category} announcements with {NUM_POSTS_PER_CATEGORY} posts")
            for i in range(0, NUM_POSTS_PER_CATEGORY, 5):  # Batch of 5
                batch_size = min(5, NUM_POSTS_PER_CATEGORY - i)
                title_prompt = f"Short title for a {category} post about cyber-crime: "
                titles = generate_text(title_prompt, max_tokens=50, batch_size=batch_size)
                contents = generate_text(random.choice(announcement_prompts), max_tokens=200, batch_size=batch_size)
                for j, (title, content) in enumerate(zip(titles, contents)):
                    ann = Announcement(
                        category=category,
                        title=title[:100],
                        content=content[:200],
                        user_id=random.choice(user_ids),
                        date=random_timestamp()
                    )
                    db.session.add(ann)
                    logger.info(f"Added {category} announcement {i + j + 1}/{NUM_POSTS_PER_CATEGORY}: {title[:30]}...")
                try:
                    db.session.commit()
                    logger.info(f"Committed {category} announcements {i + 1}-{i + batch_size}")
                except Exception as e:
                    logger.error(f"Error committing {category} announcements: {str(e)}")
                    db.session.rollback()
                    return

        # Populate Marketplace (NUM_POSTS_PER_CATEGORY per category: Buyers, Sellers)
        categories = ['Buyers', 'Sellers']
        for category in categories:
            logger.info(f"Populating {category} marketplace posts with {NUM_POSTS_PER_CATEGORY} posts")
            for i in range(0, NUM_POSTS_PER_CATEGORY, 5):  # Batch of 5
                batch_size = min(5, NUM_POSTS_PER_CATEGORY - i)
                title_prompt = f"Short title for a {category} marketplace post: "
                titles = generate_text(title_prompt, max_tokens=50, batch_size=batch_size)
                descriptions = generate_text(random.choice(marketplace_prompts), max_tokens=200, batch_size=batch_size)
                for j, (title, description) in enumerate(zip(titles, descriptions)):
                    price = f"${random.randint(50, 1000)}" if category == 'Sellers' else f"Offer ${random.randint(50, 500)}"
                    market = Marketplace(
                        category=category,
                        title=title[:100],
                        description=description[:200],
                        user_id=random.choice(user_ids),
                        price=price,
                        date=random_timestamp()
                    )
                    db.session.add(market)
                    logger.info(f"Added {category} marketplace post {i + j + 1}/{NUM_POSTS_PER_CATEGORY}: {title[:30]}...")
                try:
                    db.session.commit()
                    logger.info(f"Committed {category} marketplace posts {i + 1}-{i + batch_size}")
                except Exception as e:
                    logger.error(f"Error committing {category} marketplace posts: {str(e)}")
                    db.session.rollback()
                    return

        # Populate Services (NUM_POSTS_PER_CATEGORY per category: Buy, Sell)
        categories = ['Buy', 'Sell']
        for category in categories:
            logger.info(f"Populating {category} service posts with {NUM_POSTS_PER_CATEGORY} posts")
            for i in range(0, NUM_POSTS_PER_CATEGORY, 5):  # Batch of 5
                batch_size = min(5, NUM_POSTS_PER_CATEGORY - i)
                title_prompt = f"Short title for a {category} service post: "
                titles = generate_text(title_prompt, max_tokens=50, batch_size=batch_size)
                descriptions = generate_text(random.choice(service_prompts), max_tokens=200, batch_size=batch_size)
                for j, (title, description) in enumerate(zip(titles, descriptions)):
                    price = f"${random.randint(100, 2000)}" if category == 'Sell' else 'Negotiable'
                    service = Service(
                        category=category,
                        title=title[:100],
                        description=description[:200],
                        user_id=random.choice(user_ids),
                        price=price,
                        date=random_timestamp()
                    )
                    db.session.add(service)
                    logger.info(f"Added {category} service post {i + j + 1}/{NUM_POSTS_PER_CATEGORY}: {title[:30]}...")
                try:
                    db.session.commit()
                    logger.info(f"Committed {category} service posts {i + 1}-{i + batch_size}")
                except Exception as e:
                    logger.error(f"Error committing {category} service posts: {str(e)}")
                    db.session.rollback()
                    return

        # Populate Comments (NUM_COMMENTS_PER_POST per post)
        logger.info(f"Populating comments ({NUM_COMMENTS_PER_POST} per post)")
        announcement_ids = [(post.id, 'announcement') for post in Announcement.query.all()]
        marketplace_ids = [(post.id, 'marketplace') for post in Marketplace.query.all()]
        service_ids = [(post.id, 'service') for post in Service.query.all()]
        all_posts = announcement_ids + marketplace_ids + service_ids
        total_comments = len(all_posts) * NUM_COMMENTS_PER_POST
        for i, (post_id, post_type) in enumerate(all_posts):
            for j in range(NUM_COMMENTS_PER_POST):
                content = generate_text(random.choice(comment_prompts), max_tokens=100)[:100]
                comment = Comment(
                    post_type=post_type,
                    post_id=post_id,
                    user_id=random.choice(user_ids),
                    content=content,
                    date=random_timestamp()
                )
                db.session.add(comment)
                logger.info(f"Added comment {j + 1}/{NUM_COMMENTS_PER_POST} for {post_type} post {post_id}: {content[:30]}...")
            try:
                db.session.commit()
                logger.info(f"Committed comments for {post_type} post {i + 1}/{len(all_posts)}")
            except Exception as e:
                logger.error(f"Error committing comments for {post_type} post {post_id}: {str(e)}")
                db.session.rollback()
                return

        total_posts = NUM_POSTS_PER_CATEGORY * (len(['Announcements', 'General', 'MM Service']) + len(['Buyers', 'Sellers']) + len(['Buy', 'Sell']))
        logger.info("Database population completed successfully")
        print(f"Database initialized with 10 users, {total_posts} posts, {NUM_SHOUTBOX_MESSAGES} shoutbox messages, and {total_comments} comments.")

if __name__ == '__main__':
    init_db()
# populate_db.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Shoutbox, Announcement, Marketplace, Service, Comment
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_db():
    with app.app_context():
        db.create_all()

        # Sample data
        usernames = ['DarkHacker', 'CyberGhost', 'ShadowV', 'AnonX', 'N3tRunn3r']
        shoutbox_messages = [
            'Anyone got fresh CCs?', 'Looking for a reliable DDoS service', 'PM me for exploits',
            'New drop in marketplace!', 'Check my new service listing'
        ]
        announcement_items = [
            ('Announcements', 'Welcome to the Forum', 'Read the rules before posting.', 'Admin'),
            ('Announcements', 'New Marketplace Rules', 'All deals must be verified.', 'Admin'),
            ('General', 'Discuss latest hacks', 'Share your tools and tips.', 'DarkHacker'),
            ('MM Service', 'Escrow service available', 'Trusted middleman for deals.', 'ShadowV')
        ]
        marketplace_items = [
            ('Buyers', 'Looking for PayPal accounts', 'Need verified accounts, PM me.', 'DarkHacker', '$100'),
            ('Sellers', 'Fresh CCs for sale', 'Fullz with high balance.', 'CyberGhost', '$50'),
            ('Buyers', 'Need BTC wallets', 'Looking for high-balance wallets.', 'AnonX', '$200'),
            ('Sellers', 'Dumps for sale', 'Fresh dumps, high validity.', 'N3tRunn3r', '$75')
        ]
        services_items = [
            ('Sell', 'DDoS Service', '100Gbps attacks, reliable.', 'ShadowV', '$200/hr'),
            ('Buy', 'Need SQLi expert', 'Looking for database access.', 'AnonX', 'Negotiable'),
            ('Sell', 'Hacking service', 'Custom exploits available.', 'DarkHacker', '$500'),
            ('Buy', 'Need botnet access', 'Looking for reliable botnet.', 'CyberGhost', '$300')
        ]
        comment_items = [
            ('announcement', 1, 'AnonX', 'Thanks for the info!', '2025-07-07 13:00:00'),
            ('marketplace', 1, 'ShadowV', 'Interested, PM sent.', '2025-07-07 13:01:00'),
            ('service', 1, 'N3tRunn3r', 'Can you do 50Gbps?', '2025-07-07 13:02:00')
        ]

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for _ in range(10):
            shout = Shoutbox(
                username=random.choice(usernames),
                message=random.choice(shoutbox_messages),
                timestamp=current_time
            )
            db.session.add(shout)

        for category, title, content, username in announcement_items:
            ann = Announcement(
                category=category,
                title=title,
                content=content,
                username=username,
                date=current_time
            )
            db.session.add(ann)

        for category, title, description, username, price in marketplace_items:
            market = Marketplace(
                category=category,
                title=title,
                description=description,
                username=username,
                price=price,
                date=current_time
            )
            db.session.add(market)

        for category, title, description, username, price in services_items:
            service = Service(
                category=category,
                title=title,
                description=description,
                username=username,
                price=price,
                date=current_time
            )
            db.session.add(service)

        for post_type, post_id, username, content, date in comment_items:
            comment = Comment(
                post_type=post_type,
                post_id=post_id,
                username=username,
                content=content,
                date=date
            )
            db.session.add(comment)

        db.session.commit()
        print("Database initialized and populated.")

if __name__ == '__main__':
    init_db()

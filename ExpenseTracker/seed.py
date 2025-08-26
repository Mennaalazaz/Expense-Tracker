# this script is used to seed the database with initial data for testing purposes
# It creates 20,000 users and assigns random expenses to each user.
# Run this script separately to populate the database.
# Usage: python seed.py
# ============================================================

# from faker import Faker
# import random
# from expense import app, db
# from expense.models import User, Expense
# from werkzeug.security import generate_password_hash
# from datetime import date  as dt_date

# fake = Faker()
# def seed_data(num_users=20000, expenses_per_user=10):
#     with app.app_context():
#         db.create_all()
        
#         # Create users
#         users = db.session.query(User).all()
        
#         # Create expenses for each user
#         categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Health','Travel','Shopping','Education','Dining Out','Gifts','Donations','Others']
#         for user in users:
#             for _ in range(expenses_per_user):
#                 amount = round(random.uniform(5.0, 500.0), 2)
#                 category = random.choice(categories)
#                 date = fake.date_between(start_date=dt_date(1990, 1, 1), end_date=dt_date.today())
#                 description = fake.sentence(nb_words=6)
#                 expense = Expense(amount=amount, category=category, date=date, description=description, user_id=user.id)
#                 db.session.add(expense)
        
#         db.session.commit()
#         print(f'Seeded {num_users} users with {expenses_per_user} expenses each.')

# if __name__ == '__main__':
#     with app.app_context():
#         seed_data()
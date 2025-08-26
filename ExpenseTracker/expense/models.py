from expense import db, bcrypt , login_manager
from flask_login import UserMixin  # Import UserMixin to add user session management capabilities to the User model that manage user sessions

# This function is used to load the user from the database by its ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# constructing the User and Expense models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    @property # This is a getter method for the password attribute, which returns the hashed password.
    def password(self):
        return self.password

    @password.setter # This is a setter method for the password attribute, which hashes the password before storing it in the database.
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    # This method checks if the provided password matches the hashed password stored in the database.
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Expense('{self.amount}', '{self.category}', '{self.date}')"    


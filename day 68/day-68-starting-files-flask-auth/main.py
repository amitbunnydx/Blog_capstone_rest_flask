from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user, login_manager

from flask_login import LoginManager

login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'


# CREATE DATABASE


class Base(DeclarativeBase):
    pass


# ----- CREATE DB

sqlServerName = 'BM10890'
databaseName = 'MyMovies'
trusted_connection = 'yes'

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mssql+pyodbc://{sqlServerName}/{databaseName}"
    f"?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection={trusted_connection}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager.init_app(app)
# # Initialize DB
db = SQLAlchemy(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE TABLE IN DB with the UserMixin
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


# with app.app_context():
#     db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    # password hashing---- generate_password_hash(password, method='scrypt', salt_length=16)
    if request.method == 'POST':
        if db.session.execute(db.select(User).where(User.email == request.form.get('email'))).scalar():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
            # return render_template("register.html",value='email_issue')
        hash_and_salted_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256',
                                                          salt_length=8)
        new_user = User(
            email=request.form.get('email'),
            password=hash_and_salted_password,
            name=request.form.get('name'),
        )
        db.session.add(new_user)
        db.session.commit()

        # Log in and authenticate user after adding details to database.
        login_user(new_user)
        # return redirect(url_for("secrets",name=request.form.get('name')))
        return redirect(url_for("secrets"))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # data=db.get_or_404(User)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        connections = db.session.execute(db.select(User).where(User.email == email)).scalar()
        print(connections)
        if connections:
            if check_password_hash(connections.password, password):
                login_user(connections)
                return redirect(url_for('secrets'))
                # return render_template("secrets.html",name=current_user.name)
            else:
                flash("wrong password!")
                return render_template("login.html")
        else:
            flash("The Email does not exist, please try again!")
            return render_template("login.html")

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return render_template("index.html")


@app.route('/download', methods=['POST'])
@login_required
def download():
    print("inside ............... ")
    return send_from_directory("static", "files/cheat_sheet.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

# import relevant modules
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import string
from hashutils import make_pw_hash, check_pw_hash

# define your app
app = Flask(__name__)
app.config['DEBUG'] = True
# configure it to connect to the database
# user is blogz, database is named blogz, password is xylophone
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:xylophone@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
# create a reference to database and its methods
db = SQLAlchemy(app)
app.secret_key = 'bigglesdoingthewiggle'

# define any classes - used to construct objects, usually an entry in a table.
# So far, we've only used one class per table: User, Blog
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    visible = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.visible = True
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    email = db.Column(db.String(254), unique=True)       # change to accept emails of up to 254 characters in length
    # So apparently "backref='owner'" allows you to access properties of the user
    # through any Blog object: Blog_object.owner.username
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password, email):
        self.username = username
        self.pw_hash = make_pw_hash(password)
        self.email = email

def validate_username():
    username_error = ''                            # {0}

    # retrieve form data
    u_candidate = request.form["username"]         # {4}

    # username validation
    if len(u_candidate) == 0:
        username_error = 'Please enter a username.'
    elif ' ' in u_candidate:
        username_error = 'cannot contain spaces.'
    elif len(u_candidate) < 3 or len(u_candidate) > 20:
        username_error = 'must be between 3 and 20 characters.'
    elif u_candidate.isalnum() == False:
        username_error = 'cannot contain special characters.'

    return [u_candidate, username_error]

def validate_password():
    # password validation
    password_error = ''                            # {1}
    p_verification_error = ''                      # {2}

    # retrieve form data
    u_candidate = request.form["username"]
    p_candidate = request.form["password"]
    p_verified = request.form["password_verified"]

    if len(p_candidate) == 0:
        password_error = 'Please enter a password.'
        p_candidate = ''
        p_verified = ''
    elif ' ' in p_candidate:
        password_error = 'cannot contain spaces.'
        p_candidate = ''
        p_verified = ''
    elif len(p_candidate) < 8 or len(p_candidate) > 20:
        password_error = 'must be between 8 and 20 characters.'
        p_candidate = ''
        p_verified = ''
    elif u_candidate in p_candidate or p_candidate in u_candidate:
        password_error = 'should not be similar to usernames.'
        p_candidate = ''
        p_verified = ''
    # password matching validation
    if p_candidate != p_verified:
        p_verification_error = 'Passwords do not match.'
        p_candidate = ''
        p_verified = ''

    return [p_candidate, password_error, p_verification_error]

def validate_email():
    # email validation
    email_error = ''                               # {3}

    # retrieve form data
    e_candidate = request.form["email"]            # {5}

    if e_candidate == '':
        email_error = ''
        e_candidate = None
    elif ' ' in e_candidate:
        email_error = 'cannot contain spaces.'
    elif len(e_candidate) < 3 or len(e_candidate) > 254:
        email_error = 'must be between 3 and 254 characters.'
    elif e_candidate.count("@") != 1:
        email_error = 'must contain 1 "@" symbol.'
    elif e_candidate.count(".") < 1:
        email_error = 'must contain at least 1 "." symbol.'

    return [e_candidate, email_error]

def signup_validation():
    u_validation = validate_username()
    p_validation = validate_password()
    e_validation = validate_email()

    u_candidate = u_validation[0]
    p_candidate = p_validation[0]
    e_candidate = e_validation[0]

    u_error = u_validation[1]
    p_error = p_validation[1]
    pv_error = p_validation[2]
    e_error = e_validation[1]

    u_confirmed = ''
    p_confirmed = ''
    e_confirmed = ''

    valid = True

    # validate username
    if len(u_error) == 0:
        u_confirmed = u_candidate
    else:
        valid = False

    # validate password
    if len(p_error + pv_error) == 0:
        p_confirmed = p_candidate
    else:
        valid = False

    # validate email
    if len(e_error) == 0:
        e_confirmed = e_candidate
    else:
        valid = False

    # if valid, pass confirmed variables
    # if not valid, pass candidates with errors
    if valid == True:
        return [u_confirmed, p_confirmed, e_confirmed]
    else:
        return [u_error, p_error, pv_error, e_error, u_candidate, e_candidate]

# restrict access by requiring login
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'individual_entry', 'index']
    logged_in_routes = ['login', 'signup']
    # must include "and '/static/' not in request.path" in conditional to allow
    # CSS files to be requested. Ask about possible vulnerabilities.
    if request.endpoint not in allowed_routes and 'username' not in session and '/static/' not in request.path:
        flash('You must log in first.')
        return redirect('/login')
    elif 'username' in session and request.endpoint in logged_in_routes:
        return redirect('/blog')

# define your request handlers, one for each page
    # include any logic, say for validation or updating the database
    # return rendered templates or redirect. Don't forget to return!
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    # assigns whole object with matching username
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        entry_title = request.form['entry_title']
        entry_body = request.form['entry_body']

        title_error = ''
        body_error = ''

        if not entry_title or not entry_body:
            if not entry_title:
                title_error = "Please include a title."
            if not entry_body:
                body_error = "Please write your post here."

            return render_template('newpost.html',
            entry_title=entry_title,
            entry_body=entry_body,
            title_error=title_error,
            body_error=body_error)
        else:
            new_entry = Blog(entry_title, entry_body, owner)
            db.session.add(new_entry)
            db.session.commit()

            return redirect('/entry?q=' + str(new_entry.id))

    #if request.method == 'GET':
    return render_template('newpost.html')


@app.route('/blog')
def blog():
    user_id = request.args.get('user')

    # if there is a query
    if user_id:
        entries = Blog.query.order_by(desc(Blog.id)).filter_by(owner_id=user_id).all()
    else:
        # assigns a list of objects of class 'Blog' to 'entries' variable
            # took way to long to figure out. Apparently you have to order a select
            # before you filter it? No idea. Could swear I tried that.
        entries = Blog.query.order_by(desc(Blog.id)).filter_by(visible=True).all()

    return render_template('blog.html',
    title="Your Blog Name Here!",
    entries=entries)

@app.route('/entry')
def individual_entry():

    entry_id = request.args.get('q')
    entry = Blog.query.filter_by(id=entry_id).first()

    return render_template('individual_entry.html',
    title=entry.title,
    entry=entry)

@app.route('/delete-entry', methods=['POST'])
def delete_entry():

    # ids are usually marked as hidden on the form
    # pulls the id of the blog from the form
    entry_id = int(request.form['entry_id'])
    # assigns the result of the query, the entire matching object, to a variable
    entry = Blog.query.get(entry_id)
    entry.visible = False
    # stages the entry to the session
    db.session.add(entry)
    # commits the session to the database
    db.session.commit()

    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user_data = signup_validation()

        # redirect if all input is valid (len == 3)
        if len(user_data) == 3:
            # user data passed validation
            username = user_data[0]
            password = user_data[1]
            email = user_data[2]

            # Checks if user already exists with username or email.
            # Assigns a User object
            existing_username = User.query.filter_by(username=username).first()
            # Assigns a User object
            existing_email = User.query.filter_by(email=email).first()

            if (not existing_username and email == None) or (not existing_username and not existing_email):
                new_user = User(username, password, email)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash('Welcome, ' + username + '!')
                return redirect('/newpost')
            else:
                username_error = ''
                email_error = ''

                if existing_username:
                    username_error = 'Username already exists.'
                if existing_email:
                    email_error = 'Email Address already exists.'

                return render_template('signup.html',
                username_error=username_error,
                password_error='',
                p_verification_error='',
                email_error=email_error,
                u_candidate=username,
                e_candidate=email)

        # return errors if data is invalid (len == 6)
        elif len(user_data) == 6:
            # user data failed validation
            return render_template('signup.html',
            username_error=user_data[0],
            password_error=user_data[1],
            p_verification_error=user_data[2],
            email_error=user_data[3],
            u_candidate=user_data[4],
            e_candidate=user_data[5])

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ''
    password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # if user exists (is not NoneType) and the password is correct
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash(username + " logged in")
            return redirect('/newpost')
        else:
            if not user:
                username_error = 'User does not exist.'
            elif not check_pw_hash(password, user.pw_hash):
                password_error = 'Password is incorrect.'
            return render_template('login.html',
            username=username,
            username_error=username_error,
            password_error=password_error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    flash(session['username'] + " logged out")
    del session['username']
    return redirect('/blog')

# run the app (only if __name__ == "__main__")
if __name__ == '__main__':
    app.run()

# import relevant modules
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

# define your app
app = Flask(__name__)
app.config['DEBUG'] = True
# configure it to connect to the database
# user is build-a-blog, database is named build-a-blog, password is constructable
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
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))
    email = db.Column(db.String(120), unique=True)
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

# define your request handlers, one for each page
    # include any logic, say for validation or updating the database
    # return rendered templates or redirect. Don't forget to return!
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(id=session['user_id']).first()

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
    # assigns a list of objects of class 'Blog' to 'entries' variable
        # took way to long to figure out. Apparently you have to order a select
        # before you filter it? No idea. Could swear I tried that.
    entries = Blog.query.order_by(desc(Blog.id)).filter_by(visible=True).all()
    # entries = []

    return render_template('blog.html',
    title="Your Blog Name Here!",
    entries=entries)

    #return '<h1> display all blog posts here </h1>'

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
    return 'index page'

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return render_template('login.html', username=username)

    return render_template('login.html')

# don't forget to run the fucking app (only if __name__ == "__main__")
if __name__ == '__main__':
    app.run()

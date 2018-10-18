# import relevant modules
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

# define your app
app = Flask(__name__)
app.config['DEBUG'] = True
# configure it to connect to the database
# user is build-a-blog, database is named build-a-blog, password is constructable
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:constructable@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
# create a reference to database and its methods
db = SQLAlchemy(app)

# define any classes - used to construct objects, usually an entry in a table.
# So far, we've only used one class per table: User, Task
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    visible = db.Column(db.Boolean)

    def __init__(self, title, body, visible):
        self.title = title
        self.body = body
        self.visible = True

# define your request handlers, one for each page
    # include any logic, say for validation or updating the database
    # return rendered templates or redirect. Don't forget to return!
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

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
            new_entry = Blog(entry_title, entry_body, True)
            db.session.add(new_entry)
            db.session.commit()

            return redirect('/entry?q=' + str(new_entry.id))

    #if request.method == 'GET':
    return render_template('newpost.html')


@app.route('/')
def index():
    # assigns a list of objects of class 'Blog' to 'entries' variable
        # took way to long to figure out. Apparently you have to order a select
        # before you filter it? No idea. Could swear I tried that.
    entries = Blog.query.order_by(desc(Blog.id)).filter_by(visible=True).all()

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

# don't forget to run the fucking app (only if __name__ == "__main__")
if __name__ == '__main__':
    app.run()

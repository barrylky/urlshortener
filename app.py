import os
from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import string
from random import choices

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Migrate(app, db)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/<shorten_url>')
def redirectToOriginal(shorten_url):
    get_url = customTable.query.filter_by(shorten_url = shorten_url).first_or_404()
    return redirect(get_url.original_url)

@app.route('/addUrl', methods=['POST'])
def addUrl():
    original_url = request.form['original_url']
    new_url = customTable(original_url=original_url)
    db.session.add(new_url)
    db.session.commit()

    return render_template('add_url.html', new_link = new_url.shorten_url, original_url = new_url.original_url)

@app.route('/list')
def urlList():
    url_list = customTable.query.all()
    return render_template('list.html', url_list = url_list)

@app.errorhandler(404)
def errorPage(e):
    return render_template('404.html'), 404

######################################################
class customTable(db.Model):
    __tablename__ = 'custom'

    id = db.Column(db.Integer, primary_key = True)
    original_url = db.Column(db.String())
    shorten_url = db.Column(db.String(), unique = True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shorten_url = self.generate_short_url()

    def generate_short_url(self):
        letters = string.ascii_letters
        random_key = ''.join(choices(letters, k= 5))

        check_duplicate = self.query.filter_by(shorten_url = self.shorten_url).first()
        if check_duplicate:
            return self.generate_short_url()
        
        return random_key

if __name__ == '__main__':
    app.run(debug=True)
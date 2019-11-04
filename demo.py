import sys
import random
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import BookSearchForm
from flask import flash, render_template, request, redirect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

# Kyiv
BASECOORDS = [50.431782, 30.516382]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    latitude_off = db.Column(db.Float)
    longitude_off = db.Column(db.Float)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    district = db.relationship("District")

    def __init__(self, name, district, lat, lng):
        self.name = name
        self.district = district
        self.latitude_off = lat
        self.longitude_off = lng

    def __repr__(self):
        return f"<User:{self.id} name:{self.name} Lat:{self.latitude_off} Lng:{self.longitude_off}>"

    def get_titles(self):
        # get user's books
        book_ids = [r.id for r in db.session.query(BookInstance.id).filter_by(owner=self.id).all()]
        titles  = []
        for book_id in book_ids:
            titles.append(get_book_title_by_id(book_id))
        return titles


    @property
    def latitude(self):
        return self.latitude_off + self.district.latitude

    @property
    def longitude(self):
        return self.longitude_off + self.district.longitude


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    # author = db.Column(db.String(80))
    # tags = db.Column(db.String(80))
    # cover

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return f"< Book name:{self.title} id:{self.id}>"


class BookInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer, db.ForeignKey('book.id'))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    condition = db.Column(db.String(80))
    # price = db.Column(db.Integer)

    def __init__(self, data, owner, condition):
        self.data = data
        self.owner = owner
        self.condition = condition

    def __repr__(self):
        title = Book.query(book.c.title).filter_by(id=self.data).all()
        return f"<B_Inst:{self.id} owr:{self.owner} {title} >"


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, id, name, lat, lng):
        self.id = id
        self.name = name
        self.latitude = lat
        self.longitude = lng


def get_book_title_by_id(book_id):
    data = db.session.query(BookInstance.data).filter_by(id=book_id).one()
    title = [r.title for r in db.session.query(Book).filter_by(id=data[0]).all()]
    if title:
        return title[0]
    return 'x'


@app.route('/', methods=['GET', 'POST'])
def index():
    districts = District.query.all()
    search = BookSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', districts=districts, form=search)


@app.route('/results')
def search_results(search):
    search_string = search.data['search']
    
    if search.data['search'] != '':
        results = Book.query.filter(Book.title.contains(search_string)).all()
        for b in results:
            print(b)

    else:
        return redirect('/')

    # display results
    print('*'*80 )
    print(f'found {len(results)}')
    print(f'results = {results}')
    for b in results:
        print(b)

        return render_template('results.html', results=results)


@app.route('/district/<int:district_id>')
def district(district_id):
    users = User.query.filter_by(district_id=district_id).all()

    # create list of ghf users books (for fun)
    for user in users:
        booklist = []
        users = User.query.filter_by(district_id=district_id).all()
    coords = [[user.latitude, user.longitude, str(user.get_titles())] for user in users]
    print('_' * 80)
    return jsonify({"data": coords})


def make_random_data(db):
    # generate random users
    N_DISTRICTS = 1
    N_USERS = 10
    BOOK_NAMES = ['Kerry', 'Bible', 'Bible 2', 'Tom Sawer',
                'Jungle book', 'Cinderella', 'Birdwatcher', 'Matrix',
                'Forest Gump', 'Breakfast for champions']
    N_BOOKS = len(BOOK_NAMES) * 4
    for distr_id in range(N_DISTRICTS):
        district = District(distr_id, "District %d" % distr_id, BASECOORDS[0], BASECOORDS[1])
        db.session.add(district)
        for user_id in range(N_USERS):
            name = 'usr:' + str(user_id)
            lat = random.random() - 0.5
            lng = random.random() - 0.5
            row = User(name, district, lat, lng)

            db.session.add(row)
    db.session.commit()


    # create list of Books
    for book_id in range(len(BOOK_NAMES)):
        row =  Book(BOOK_NAMES[book_id])
        db.session.add(row)
    db.session.commit()

    # create Book Instances
    all_user_ids = [r.id for r in db.session.query(User.id)]  # get all users indecies
    print(f'Total all_user_ids = {len(all_user_ids)}')

    all_book_ids = [r.id for r in db.session.query(Book.id)]
    print(all_book_ids)
    print(f'Total all_book_ids = {len(all_book_ids)}')

    for i in range(N_BOOKS):
        row = BookInstance(random.choice(all_book_ids), random.choice(all_user_ids), 'OK')
        print(random.choice(all_book_ids), random.choice(all_user_ids))
        db.session.add(row)
    db.session.commit()

    all_book_inst_ids = [r.id for r in db.session.query(BookInstance.id)]
    print(f'Total all_book_inst_ids = {len(all_book_inst_ids)}')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    if len(sys.argv) > 1:
        if sys.argv[1] == 'mkdb':
            db.create_all()
            make_random_data(db)
    else:
        app.run(debug=True)

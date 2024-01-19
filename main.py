from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests


class UpdateForm(FlaskForm):
    rating_input = FloatField(label='Your rating out of 10')
    review_input = StringField(label='Your review')
    submit = SubmitField(label="Done")
    
    
class AddForm(FlaskForm):
    title = StringField("Movie name", validators=[DataRequired()])
    submit = SubmitField(label="Add")


API_KEY = "bb48572ae395180e97e7ba81d76f8006"
API_TOKEN = ("eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiYjQ4NTcyYWUzOTUxODBlOTdlN2JhODFkNzZmODAwNiIsInN1YiI6IjY1OGFlNmE2NGRhM"
             "2Q0NjY0NDQxMmE0ZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.RM5QD8bnO30PYIua0Off8nTaZsobEYsrBO8"
             "DKB9gGcQ")


headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}





'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


db = SQLAlchemy()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-project.db"

db.init_app(app)


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


# new_movie = Movies(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
#
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.commit()


@app.route("/")
def home():
    all_movie = db.session.execute(db.select(Movies).order_by(Movies.rating.desc())).scalars().all()
    for i in range(len(all_movie)):
        all_movie[i].ranking = i+1
    return render_template("index.html", movies=all_movie)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    update_form = UpdateForm()
    if update_form.validate_on_submit():
        rating = update_form.rating_input.data
        review = update_form.review_input.data
        movie_id = request.args.get('id')
        movie_to_update = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
        # or movie_to_update = db.get_or_404(Book, book_id)
        movie_to_update.rating = rating
        if review != "":
            movie_to_update.review = review
        db.session.commit()
        return redirect(url_for('home'))
    else:
        movie_id = request.args.get('id')
        movie = db.get_or_404(Movies, movie_id)
        return render_template("edit.html", form=update_form, movie=movie)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
    # or movie_to_delete = db.get_or_404(Book, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    add_form = AddForm()
    if add_form.validate_on_submit():
        movie_name = add_form.title.data
        parameters = {
            'query': movie_name,
            'include_adult': 'true',
            'language': 'en-US',
            'page': 1
        }
        url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
        response = requests.get(url=url, headers=headers, params=parameters)
        movie_list = response.json()["results"]
        return render_template("select.html", movie_list=movie_list)
    else:
        return render_template("add.html", form=add_form)


@app.route("/entry")
def entry():
    movie_id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    response = requests.get(url, headers=headers)
    movie_data = response.json()
    new_movie = Movies(
        title=movie_data['title'],
        year=movie_data['release_date'].split("-")[0],
        description=movie_data['overview'],
        rating=0,
        ranking=0,
        review="None",
        img_url=f"https://image.tmdb.org/t/p/w300/{movie_data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)

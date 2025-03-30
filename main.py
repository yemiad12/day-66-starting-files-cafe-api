
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, make_url
import os
# from dotenv import load_dotenv  # Install: pip install python-dotenv
import psycopg2
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.testing.util import random_choices

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass

# load_dotenv()  # Load the .env file

# database_url = os.environ.get("DATABASE_URL")

database_url = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

api_key = os.environ.get("API_KEY")

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] =f"{database_url}"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

API_KEY = f"{api_key}"


# print(f"Database URL: {database_url}")
# print(f"API Key: {api_key}")

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


class FlaskForm:
    pass


class StringField:
    pass


class DataRequired:
    pass



@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
# @app.route("/random", methods=["GET"])
# def get_random_cafe():
#   pass

## But GET is allowed by default on all routes.
# So this is much simpler:
all_cafes = []
random_values = {}
@app.route("/random")
def get_random_cafe():
    with app.app_context():
        global random_values
        global all_cafes
        result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
        # result = db.session.execute(db.select(Books).where(Books.id == 2))
        all_cafes = result.scalars().fetchall()
        random_cafe = random_choices(all_cafes)
        print(random_cafe)
        for cafe in random_cafe:
            random_values ["name"] = cafe.name
            random_values ["location"] = cafe.location

    return jsonify(cafe=random_values)


all_values = {}


@app.route("/all")
def get_all():
    all_items = []
    with app.app_context():
        global random_values
        global all_cafes
        global all_values

        result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
        # result = db.session.execute(db.select(Books).where(Books.id == 2))
        all_cafes = result.scalars().fetchall()
        random_cafe = random_choices(all_cafes)
        print(all_cafes)
        for cafe in all_cafes:
            cafe_row = {"name": cafe.name, "location": cafe.location}
            if cafe_row:
                all_items.append(cafe_row)


    return jsonify(cafes=all_items)


@app.route("/search", methods=['GET', 'POST'])
def search():
    search_items = []
    search_info = request.args.get('loc')
    print(search_info)
    with app.app_context():
        global random_values
        result = db.session.execute(db.select(Cafe).order_by(Cafe.id).where(Cafe.location == search_info))
        # result = db.session.execute(db.select(Books).where(Books.id == 2))
        search_result = result.scalars().fetchall()
        print(search_result)
        error_message = {"Not Found": "Sorry, we don't have a cafe at that location."}
        for cafe in search_result:
            cafe_row = {"name": cafe.name, "location": cafe.location}
            if cafe_row:
                search_items.append(cafe_row)


    if search_items:
        return jsonify(cafes=search_items)
    else:
        return jsonify(error=error_message)

# HTTP POST - Create Record
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = request.form
    cafe_name = form["name"]
    cafe_map_url = form["map_url"]
    cafe_img_url = form["img_url"]
    cafe_location = form["location"]
    cafe_seats = form["seats"]
    cafe_has_toilet = bool(form["has_toilet"])
    cafe_has_wifi = bool(form["has_wifi"])
    cafe_has_sockets = bool(form["has_sockets"])
    cafe_can_take_calls = bool(form["can_take_calls"])
    cafe_coffee_price = form["coffee_price"]


    with app.app_context():
        record = Cafe(name=cafe_name, map_url=cafe_map_url, img_url=cafe_img_url, location=cafe_location,
                      seats=cafe_seats, has_toilet=cafe_has_toilet, has_wifi=cafe_has_wifi, has_sockets=cafe_has_sockets,
                      can_take_calls=cafe_can_take_calls, coffee_price=cafe_coffee_price)
        db.session.add(record)
        db.session.commit()
        success_message = {"Success": "Successfully added the new cafe."}


    return jsonify(success=success_message)

# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    global all_cafes
    search_id = cafe_id
    print(search_id)
    new_coffee_price = request.args.get('new_price')
    print(new_coffee_price)
    error_message = {"Not Found": "Sorry, we don't have a cafe at that location."}
    with app.app_context():
        update = db.session.execute(db.select(Cafe).where(Cafe.id == search_id)).scalar()
        print(update)
        if update:
            update.coffee_price = new_coffee_price
            print(update.coffee_price)
            db.session.commit()
            print(db.session.commit())
            success_message = {"Success": "Successfully added the new cafe."}
            return jsonify(success=success_message)
    #
    #
    # result = db.session.execute(db.select(Cafe).where(Cafe.id == search_id)).scalar()
    #
    # if result.coffee_price == new_coffee_price:
    #
    # else:
    return jsonify(error=error_message)

# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete(cafe_id):
    global all_cafes
    global API_KEY
    search_id = cafe_id
    print(search_id)
    api_key = request.args.get('api_key')
    print(api_key)
    api_key_error_message = {"Error": "Sorry, that's not allowed. Make sure you have the correct api_key."}
    error_message = {"Not Found": "Sorry, we don't have a cafe at that location."}
    attribute_error = {"Attribute Error": "Sorry, we don't have a cafe at that location."}


    if api_key != API_KEY:
        return jsonify(error=api_key_error_message)
    # try:
    #     with app.app_context():
    #         result = db.session.execute(db.select(Cafe).where(Cafe.id == search_id)).scalar()
    #         print(search_id)
    #         print(result.id)
    #     if result.id != search_id:
    #         return jsonify(error=error_message)
    # except AttributeError:
    #     return jsonify(error=attribute_error)

    try:
        with app.app_context():
            delete_row = db.session.execute(db.select(Cafe).where(Cafe.id == search_id)).scalar()
            db.session.delete(delete_row)
            db.session.commit()
            success_message = {"Success": "Successfully deleted the cafe."}
            return jsonify(success=success_message)
    except (AttributeError, UnmappedInstanceError):
        return jsonify(error=attribute_error)




if __name__ == '__main__':
    app.run(debug=False)

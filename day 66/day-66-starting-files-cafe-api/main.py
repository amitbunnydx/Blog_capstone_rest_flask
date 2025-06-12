import random

from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

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

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

#----- CREATE DB

sqlServerName = 'BM10890'
databaseName = 'MyMovies'
trusted_connection = 'yes'

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mssql+pyodbc://{sqlServerName}/{databaseName}"
    f"?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection={trusted_connection}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db = SQLAlchemy(app)

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(5000), nullable=False)
    img_url: Mapped[str] = mapped_column(String(5000), nullable=False)
    location: Mapped[str] = mapped_column(String(2500), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


# with app.app_context():
#     db.create_all()
    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            # print(getattr(self, column.name))
            dictionary[column.name] = getattr(self, column.name)
            print(dictionary)
        # print(dictionary)
        return dictionary

        # Method 2. Alternatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():#http://127.0.0.1:5000/random
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    # print(all_cafes)
    random_cafe = random.choice(all_cafes)
    # for main_cafe in all_cafes:
    #     print(main_cafe)
    #     print(cafe=main_cafe.to_dict())
    # return None
    return jsonify(cafe=random_cafe.to_dict())
    # return jsonify(cafe={
    #     #Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     #Put some properties in a sub-category
    #     "amenities": {
    #       "seats": random_cafe.seats,
    #       "has_toilet": random_cafe.has_toilet,
    #       "has_wifi": random_cafe.has_wifi,
    #       "has_sockets": random_cafe.has_sockets,
    #       "can_take_calls": random_cafe.can_take_calls,
    #       "coffee_price": random_cafe.coffee_price,
    #     }
    # })

@app.route("/all")
def get_all_cafes():#http://127.0.0.1:5000/all
    result=db.session.execute(db.select(Cafe))
    all_cafe=result.scalars().all()
    print(all_cafe)
    return jsonify(allCaffe=[cafe.to_dict() for cafe in all_cafe])


@app.route('/search')
def get_cafe_at_location():#http://127.0.0.1:5000/search?loc=mumbai
    query_location = request.args.get("loc")
    # print(query_location)
    # print(db.select(Cafe).where(Cafe.location==query_location))
    result=db.session.execute(db.select(Cafe).where(Cafe.location==query_location))
    print(result)
    all_cafes=result.scalars().all()
    print(all_cafes)
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route('/add',methods=["POST"])
def post_new_cafe():
    new_cafe=Cafe(
    name=request.form.get("name"),
    map_url=request.form.get("map_url"),
    img_url=request.form.get("img_url"),
    location=request.form.get("location"),
    seats=request.form.get("seats"),
    has_toilet=bool(request.form.get("has_toilet")),
    has_wifi=bool(request.form.get("has_wifi")),
    has_sockets=bool(request.form.get("has_sockets")),
    can_take_calls=bool(request.form.get("can_take_calls")),
    coffee_price=request.form.get("coffee_price"),
    )
    # print(type(new_cafe.has_toilet))
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success":"Successfully added the new cafe"})

# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>',methods=["PATCH"])#http://127.0.0.1:5000/update-price/6?new_coffee_price=100
def patch_cafe(cafe_id):
    print(cafe_id)
    new_coffee_price = request.args.get("new_coffee_price")
    print(new_coffee_price)
    try:
        print("in try")
        # cafe = db.get(Cafe, cafe_id)
        cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        print(cafe.coffee_price)
        print("out try")
        # all_cafes = cafe.scalars().all()
        # print(all_cafes.coffee_price)
        print(cafe)
    except AttributeError:
        print("in except")
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        print("in else")
        cafe.coffee_price = new_coffee_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200

# HTTP DELETE - Delete Record
@app.route('/report_close/<cafe_id>',methods=['DELETE'])#http://127.0.0.1:5000/report_close/3?TopSecretKay=TopSecretAPIKey
def delete_cafe(cafe_id):
    secret_key=request.args.get('TopSecretKay')
    print(secret_key)
    if secret_key == "TopSecretAPIKey":
        try:
            cafe=db.session.execute(db.select(Cafe).where(Cafe.id==cafe_id)).scalar()
            if cafe is None:
                print("in delete process")
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        except AttributeError:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        else:
            print("in else")
            print("in delete process")
            # db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Record is Successfully deleted ."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry that now allow make sour you have correct api_key."}), 404


if __name__ == '__main__':
    app.run(debug=True)

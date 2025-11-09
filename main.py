from flask import Flask, render_template, redirect, url_for, request
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean
import random
from forms import CreateForm
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


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


@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe))
    cafe_list = result.scalars().all()
    filter_command = request.args.get("filter_command")
    match filter_command:

        case "wifi":
            cafe_list = [cafe for cafe in cafe_list if cafe.has_wifi == 1]

        case "sockets":
            cafe_list = [cafe for cafe in cafe_list if cafe.has_sockets == 1]

        case "toilet":
            cafe_list = [cafe for cafe in cafe_list if cafe.has_toilet == 1]

        case "calls":
            cafe_list = [cafe for cafe in cafe_list if cafe.can_take_calls == 1]

        case _:
            pass

    cafes_found = len(cafe_list)

    return render_template("index.html", cafe_list=cafe_list, cafes_found=cafes_found)


@app.route("/add", methods=["POST", "GET"])
def add():
    form = CreateForm()
    if form.validate_on_submit():
        name = form.data.get("name")
        map_url = form.data.get("map_url")
        img_url = form.data.get("img_url")
        location = form.data.get("location")
        has_sockets = form.data.get("has_sockets")
        has_toilet = form.data.get("has_toilet")
        has_wifi = form.data.get("has_wifi")
        can_take_calls = form.data.get("can_take_calls")
        seats = form.data.get("seats")
        coffee_price = form.data.get("coffee_price")

        if db.session.execute(db.select(Cafe).where(Cafe.name == name)).scalar() is None:
            cafe = Cafe(
                name=name,
                map_url=map_url,
                img_url=img_url,
                location=location,
                has_sockets=has_sockets,
                has_toilet=has_toilet,
                has_wifi=has_wifi,
                can_take_calls=can_take_calls,
                seats=seats,
                coffee_price=coffee_price,
            )
            db.session.add(cafe)
            db.session.commit()
            return redirect(url_for("home"))

    return render_template("Form.html", form=form)


@app.route("/<name>")
def place(name):
    if name == "random":
        print("yes")
        result = db.session.execute(db.select(Cafe))
        cafe_list = result.scalars().all()
        cafe = random.choice(cafe_list)
        return redirect(url_for("place", name=cafe.name))

    result = db.session.execute(db.select(Cafe).where(Cafe.name == name)).scalar()
    return render_template("cafe_page.html", cafe=result)


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()

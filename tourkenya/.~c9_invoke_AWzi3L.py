from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from time import strftime
from helpers import apology, login_required, lookup, usd
import wikipedia
from bs4 import BeautifulSoup
import requests
import pdfkit
# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tourkenya.db")

@app.route("/description", methods=["POST"])
def description():
    if request.method == "POST":
        key = request.form.get("name")
        summary = wikipedia.summary(key)
        page = wikipedia.page(key)

        resorts = db.execute("SELECT * FROM resorts WHERE place=:name",
                            name = key)
        wildlife = db.execute("SELECT * FROM wildlife WHERE name = :name",
                            name = key)
        resort_list = list()
        wildlife_list = []
        for resort in resorts:
            temp = dict()
            temp["name"]=resort["hotel_name"]
            temp["image1"]=resort["imageA"]
            temp["image2"]=resort["imageB"]
            temp["price"]=resort["price"]
            temp['id']=resort["id"]
            resort_list.append(temp)

        for row in wildlife:
            temp = {}
            temp["name"]=row["name"]
            temp["image1"]=row["image1"]
            temp["image2"]=row["image2"]
            temp["youtube"]=row["youtube"]
            temp["wikipedia"]=row['wikipedia']
            wildlife_list.append(temp)



        return render_template("test.html", summary = summary,name = page.title, resorts = resort_list, wildlife=wildlife_list)

# @app.route("/")
# def index():
#     return render_template("index.html")

@app.route("/")
def home():
    wildlife = db.execute("SELECT * FROM wildlife")
    resorts = db.execute("SELECT * FROM resorts")

    wildlife_list = list()
    resort_list = list()

    for item in wildlife:
        temp_dict = dict()
        temp_dict['name'] = item['name']
        temp_dict['image1'] = item['image1']
        temp_dict['image2'] = item['image2']
        wildlife_list.append(temp_dict)

    for item in resorts:
        temp_dict = dict()
        temp_dict['name'] = item['hotel_name']
        temp_dict['image1'] = item['imageA']
        temp_dict['image2'] = item['imageB']
        resort_list.append(temp_dict)




    return render_template("home.html", wildlife_list=wildlife_list, resort_list=resort_list)

@app.route("/profile")
@login_required
def profile():
    """Show users profile"""
    # select username from database
    username = db.execute("SELECT username FROM users where id = :session",
                          session=session["user_id"])

    # select all information about the user
    user_info = db.execute("SELECT * FROM users WHERE id = :session",
                        session=session["user_id"])

    index = dict()

    # iterate through selected items in database
    # print rows in table
    for user in user_info:
        # check for sold out stocks
        index['username'] = user['username']
        index['email'] = user['email']
        index['country'] = user['country']
        index['city'] = user['city']
        index['address'] = user['address']
        index['phone'] = user['phone']
        index['profile_picture'] = user['profile_picture']

    # pass rows to html
    return render_template("profile.html", index=index)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/profile")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("log-in.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote")
@login_required
def quote():
    """Get stock quote."""


    # lookup current stock price
    data = requests.get('http://www.magicalkenya.com/places-to-visit/wilderness-areas/masai-mara-game-reserve/')
    text = data.content
    soup = BeautifulSoup(text, 'html.parser')

    return render_template("quoted.html" ,text=soup)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # check for correct usage
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("please confirm password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # insert new user into database
        rows = db.execute("INSERT INTO users (username, hash, email, country, city, address, phone) VALUES(:username, :hash, :email, :country, :city, :address, :phone)",
                          username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")), email=request.form.get("email"), country=request.form.get("country"), city=request.form.get("city"), address=request.form.get("address"), phone=request.form.get("phone"))
        # check if user already exists
        if not rows:
            return apology("username already exists")

        # store user id
        session["user_id"] = rows

        return redirect("/profile")
    else:
        return render_template("log-in.html")

@app.route("/tourcompany", methods=["POST"])
@login_required
def tourcompany():
    safari_days = request.form.get("safari_days")
    company = request.form.get("company")

    company_details = db.execute("SELECT * FROM companies WHERE name = :company",
                             company = company)
    safari_total = company_details[0]["rate"] * float(safari_days)

    current_total = db.execute("SELECT total FROM cart WHERE user_id = :user_id",
                              user_id=session["user_id"])
    total = safari_total + current_total[0]["total"]

    db.execute("UPDATE cart SET company = :company, safari_total = :safari_total, safari_days = :safari_days, total = :total",
              company=company, safari_total=safari_total, safari_days = safari_days, total=total)

    cart_details = db.execute("SELECT * FROM cart WHERE user_id = :user_id",
                              user_id=session["user_id"])

    resort = cart_details[0]["resort"]
    attraction = cart_details[0]["attraction"]
    hotel_days = cart_details[0]["hotel_days"]
    hotel_total = cart_details[0]["hotel_total"]

    return render_template("cart.html", safari_days=safari_days, company=company, safari_total=safari_total, total=total, resort=resort, attraction=attraction, hotel_days=hotel_days, hotel_total=hotel_total)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        hotel_id = int(request.form.get("hotel_id"))
        hotel_days = int(request.form.get("hotel_days"))

        resort_details = db.execute("SELECT * from resorts WHERE id = :hotel_id",
                                    hotel_id=hotel_id)

        hotel_price=resort_details[0]["price"]
        hotel_name = resort_details[0]["hotel_name"]
        hotel_total = hotel_price * hotel_days
        total = hotel_total
        attraction = resort_details[0]["place"]

        if not db.execute("SELECT * FROM cart WHERE user_id = :id",
                          id=session["user_id"]):

            db.execute("INSER INTO cart (user_id, hotel_days, hotel_total, total, attraction, resort) VALUES (:user_id, :hotel_days, :hotel_total, :total, :attraction, :resort)",
               user_id = session["user_id"], hotel_days=hotel_days, hotel_total=hotel_total, total=total, attraction=attraction, resort=hotel_name)
        else:
            db.execute("UPDATE cart SET hotel_days = :hotel_days, hotel_total = :hotel_total, total = :total, attraction = :attraction, resort = :resort",
                       hotel_days=hotel_days, hotel_total=hotel_total, total=total, attraction=attraction, resort=hotel_name)


        companies = db.execute("SELECT * from companies")

        company_list = list()

        for company in companies:
            temp_dict = dict()
            temp_dict["name"] = company["name"]
            temp_dict["image1"] = company["image1"]
            temp_dict["rate"] = company["rate"]

            company_list.append(temp_dict)

        return render_template("tourcompany.html", company_list=company_list)

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    return render_template("payment.html")
@app.route("/receipt", methods=["POST"])
@login_required
def receipt():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    address1 = request.form.get("address1")
    address2 = null
    if request.form.get("address2"):
        address2= request.form.get("address2")
    city = request.form.get("city")
    state = request.form.get("state")
    zip = request.form.get("zip")

    cart_details = db.execute("SELECT * FROM cart WHERE user_id = :user_id",
                              user_id=session["user_id"])

    attraction = cart_details[0]["attraction"]
    accomodation = cart_details[0]["resort"]
    hotel_days = cart_details[0]["hotel_days"]
    safari_days = cart_details[0]["safari_days"]
    tour_guide = cart_details[0]["company"]
    total = cart_details[0]["total"]

    return render_template("receipt.html", attraction=attraction, accomodation=accomodation, hotel_days=hotel_days, safari_days=safari_days, tour_guide=tour_guide, total=total,
                           first_name=first_name, last_name=last_name, email=email, address1=address1, address2=address2, city=city, state=state, zip=zip)


@

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

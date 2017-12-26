from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from time import strftime
from helpers import apology, login_required, lookup, usd
import wikipedia
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
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


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tourkenya.db")


@app.route("/description", methods=["POST"])
def description():
    """Show information related to the destination the user selected"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Obtain a wikipedia summary from the name the user inputs
        key = request.form.get("name")
        summary = wikipedia.summary(key)
        page = wikipedia.page(key)

        # Select all resorts in the database near the place the user selected
        resorts = db.execute("SELECT * FROM resorts WHERE place=:name",
                             name=key)

        # Select info about the place the user selected from the database
        wildlife = db.execute("SELECT * FROM wildlife WHERE name = :name",
                              name=key)

        # Select 3 tour packages related to the place the user selected
        packages = db.execute("SELECT * FROM packages WHERE place = :place ORDER BY RANDOM() LIMIT 3",
                              place=key)
        # Select all the tour guide companies from the database
        companies = db.execute("SELECT * FROM companies")

        ratings = db.execute("SELECT hotel_name, ratings FROM resorts WHERE place=:name",
                             name=key)

        company_list, resort_list, wildlife_list, packages_list = [], [], [], []

        # Create lists of dicts out of the information selected from the tables in the databases
        for resort in resorts:
            temp = dict()
            temp["name"] = resort["hotel_name"]
            temp["image1"] = resort["imageA"]
            temp["image2"] = resort["imageB"]
            temp["price"] = resort["price"]
            temp["description"] = resort["description"]
            temp["ratings"] = resort["ratings"]
            temp["website"] = resort["website"]
            temp['id'] = resort["id"]
            resort_list.append(temp)

        for company in companies:
            temp = dict()
            temp["name"] = company["name"]
            temp["image1"] = company["image1"]
            temp["description"] = company["Description"]
            temp["ratings"] = company["Ratings"]
            temp["price"] = company["rate"]
            temp["website"] = company["website"]
            temp['id'] = company["id"]
            company_list.append(temp)

        for row in wildlife:
            temp = {}
            temp["name"] = row["name"]
            temp["image1"] = row["image1"]
            temp["image2"] = row["image2"]
            temp["youtube"] = row["youtube"]
            temp["wikipedia"] = row['wikipedia']
            wildlife_list.append(temp)

        for item in packages:
            temp = {}
            temp["price"] = item["price"]
            temp["original"] = item["price"] + 50
            temp["place"] = item["place"]
            temp["hotel"] = item["hotel"]
            temp["company"] = item["company"]
            temp["id"] = item["id"]
            temp["image1"] = wildlife[0]["image1"]

            packages_list.append(temp)

    # This code was used to simplify creation of packages from a combination of company, resort and wildlife places
        # charge = 20
        # for resort in resort_list:
        #     for company in company_list:
        #         temp={}
        #         temp["cost"] = resort['price'] + company['price'] + charge
        #         temp["place"] = key
        #         temp['company'] = company["name"]
        #         temp["hotel"] = resort ["name"]

        #         db.execute("INSERT INTO packages (price, place, hotel, company) VALUES (:price, :place, :hotel, :company)",
        #                     price = temp['cost'], place=temp['place'],company=temp['company'],hotel=temp['hotel'])

        # Render a page with descriptions passing to it all the relevant information
        return render_template("test.html", ratings= jsonify(ratings),summary = summary,name = page.title, resorts = resort_list, wildlife=wildlife_list,companies=company_list, packages=packages_list)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/hotel-description", methods=["POST"])
def hotels():
    """ Displays relevant information pertaining to a particulat hotel"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Store name of hotel the user has selected in a variable
        key = request.form.get("name")

        # Select info for the resort the user selected
        resorts = db.execute("SELECT * FROM resorts WHERE hotel_name=:key",
                             key=key)
        # Select all the tour guide companies
        companies = db.execute("SELECT * FROM companies")

        ratings = db.execute("SELECT ratings FROM resorts WHERE hotel_name=:key",
                             key=key)
        packages = db.execute("SELECT * FROM packages WHERE hotel = :hotel ORDER BY RANDOM() LIMIT 3",
                              hotel=key)

        # Store all the selected information in lists that will passed to html
        company_list, resort_list, wildlife_list, packages_list = [],[],[],[]

        for resort in resorts:
            temp = dict()
            temp["name"] = resort["hotel_name"]
            temp["image1"] = resort["imageA"]
            temp["image2"] = resort["imageB"]
            temp["price"] = resort["price"]
            temp["description"] = resort["description"]
            temp["ratings"] = resort["ratings"]
            temp["website"] = resort["website"]
            temp["place"] = resort["place"]
            temp['id'] = resort["id"]
            resort_list.append(temp)

        for company in companies:
            temp = dict()
            temp["name"] = company["name"]
            temp["image1"] = company["image1"]
            temp["description"] = company["Description"]
            temp["ratings"] = company["Ratings"]
            temp["price"] = company["rate"]
            temp["website"] = company["website"]
            temp['id'] = company["id"]
            company_list.append(temp)

        for resort in resort_list:
            temp = {}
            place = resort["place"]
            wildlife = db.execute("SELECT * FROM wildlife WHERE name = :name",
                                  name = place)
            for row in wildlife:
                temp = {}
                temp["name"] = row["name"]
                temp["image1"] = row["image1"]
                temp["image2"] = row["image2"]
                temp["youtube"] = row["youtube"]
                temp["wikipedia"] = row['wikipedia']
                temp["description"] = wikipedia.summary(place)
                wildlife_list.append(temp)

        for item in packages:
            temp = {}
            temp["price"] = item["price"]
            temp["original"] = item["price"] + 50
            temp["place"] = item["place"]
            temp["hotel"] = item["hotel"]
            temp["company"] = item["company"]
            temp["id"] = item["id"]
            temp["image1"] = wildlife[0]["image1"]

            packages_list.append(temp)

        # Render template with all relevant information for a particular hotel
        return render_template("hotel-description.html", ratings=jsonify(ratings), name=key, resorts=resort_list, companies=company_list, wildlife=wildlife_list, packages=packages_list)

@app.route("/home")
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
    """Show user's profile"""
    # Select username from database
    username = db.execute("SELECT username FROM users where id = :session",
                          session=session["user_id"])

    # Select all information about the user
    user_info = db.execute("SELECT * FROM users WHERE id = :session",
                           session=session["user_id"])

    index = dict()

    # Add user details to a dict
    for user in user_info:
        index['username'] = user['username']
        index['email'] = user['email']
        index['country'] = user['country']
        index['city'] = user['city']
        index['address'] = user['address']
        index['phone'] = user['phone']
        index['profile_picture'] = user['profile_picture']

    # pass dict to html
    return render_template("user-profile.html", index=index)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            message = "Invalid username or password"
            return render_template("log-in.html", message=message)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("log-in.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")


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
        # User reached route via GET(as by clicking a link or via redirect)
        return render_template("log-in.html")


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    """ Cart having all packages a user is interested in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Obtain the start and end date of trip and calculate number of days of trip from it
        start_date = datetime.strptime(request.form.get("start-date"), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get("end-date"), '%Y-%m-%d')
        days = abs(start_date - end_date).days

        # Obtain number of people travelling in the trip and the id of the selected trip package
        people = int(request.form.get("people"))
        packageId = request.form.get("id")

        # Select from the packages table, all information about the selected package
        package_details = db.execute("SELECT * FROM packages WHERE id = :id",
                                     id=packageId)

        attraction = package_details[0]["place"]
        resort = package_details[0]["hotel"]
        safari_days = days
        price = package_details[0]["price"] * people * days
        company = package_details[0]["company"]
        package_id = packageId
        user_id = session["user_id"]
        people_number = people

        # Insert package into cart
        db.execute("INSERT into cart(attraction, resort, safari_days, price, company, user_id, package_id, people) VALUES (:attraction, :resort, :safari_days, :price, :company, :user_id, :package_id, :people)",
                   attraction=attraction, resort=resort, safari_days=safari_days, price=price, company=company, user_id=user_id, package_id=package_id, people=people_number)

        # Ensure no refresh
        return ("", 204)


    else:
        # User reached route via GET (as by clicking a link or via redirect)
        cart_details = db.execute("SELECT * FROM cart WHERE user_id = :user_id",
                                  user_id=session["user_id"])

        # Show cart details only if the user has items in the cart
        if cart_details:

            # Create a list from all the packages in a user's cart
            cart_list = list()

            # Append the packages to the list
            for item in cart_details:
                temp = dict()

                temp["attraction"] = item["attraction"]
                temp["resort"] = item["resort"]
                temp["safari_days"] = item["safari_days"]
                temp["price"] = item["price"]
                temp["company"] = item["company"]
                temp["package_id"] = item["package_id"]
                temp["people"] = item["people"]

                cart_list.append(temp)

            # Render cart html passing all the packages in user's cart
            return render_template("cart.html", cart_list=cart_list)

        else:
            # If the user has no packages in cart
            return render_template("empty-cart.html")


@app.route("/remove_item", methods=["GET", "POST"])
@login_required
def remove_item():
    """ Removes a package from the cart"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Remove package from cart table using its id
        package_id = int(request.form.get("id"))
        db.execute("DELETE FROM cart WHERE user_id = :user_id AND package_id = :package_id",
                   user_id=session["user_id"], package_id=package_id)

        return redirect("/cart")


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """ Display payment page"""
    package_id = int(request.form.get("id"))

    return render_template("payment.html", package_id=package_id)


@app.route("/receipt", methods=["POST"])
@login_required
def receipt():
    """ Display a receipt to the user """
    # Obtains billing information from the payment page
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    address1 = request.form.get("address1")
    address2 = "null"
    if request.form.get("address2"):
        address2 = request.form.get("address2")
    city = request.form.get("city")
    state = request.form.get("state")
    zip = request.form.get("zip")

    # Obtain the package id
    package_id = int(request.form.get("id"))

    # Select from the cart table information about the particular package
    cart_details = db.execute("SELECT * FROM cart WHERE user_id = :user_id and package_id = :package_id",
                              user_id=session["user_id"], package_id=package_id)

    attraction = cart_details[0]["attraction"]
    accomodation = cart_details[0]["resort"]
    tour_guide = cart_details[0]["company"]
    safari_days = cart_details[0]["safari_days"]
    people = cart_details[0]["people"]
    total = cart_details[0]["price"]

    # Remove item from cart aftewards
    db.execute("DELETE FROM cart WHERE user_id = :user_id AND package_id = :package_id",
               user_id=session["user_id"], package_id=package_id)

    # Render a receipt template passing all neccessary fields
    return render_template("receipt.html", attraction=attraction, accomodation=accomodation, people=people, safari_days=safari_days, tour_guide=tour_guide, total=total,
                           first_name=first_name, last_name=last_name, email=email, address1=address1, address2=address2, city=city, state=state, zip=zip)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)



# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/ratings")
def ratings():
    q = request.args.get("name")
    ratings = db.execute("SELECT hotel_name, ratings FROM resorts WHERE place=:name",
                         name=q)

    return jsonify(ratings)


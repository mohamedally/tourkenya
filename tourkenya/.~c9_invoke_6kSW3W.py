from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from time import strftime
from helpers import apology, login_required, lookup, usd
import wikipedia

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
        resorts = db.execute("SELECT * FROM resorts JOIN wildlife ON resorts.attraction = wildlife.id WHERE name LIKE '%:name%'",
                            name = key)
        resort_list = []
        for resort in resorts:
            temp = {}
            temp["name"]=resort["name"]
            temp["image1"]=resort["image1"]
            temp["image2"]=resort["image2"]
            temp["price"]=resort["price"]
            resort_list.append(temp)

        attractions = db.execute("SELECT name FROM wildlife")
        attraction_list = list()

        for attraction in attractions:
            temp = dict()
            temp["name"] = attraction["name"]
            attraction_list.append(temp)

        return render_template("test.html", summary = summary, images=page.images,name = page.title, resorts = resort_list, attraction_list=attraction_list)

@app.route("/")
@login_required
def index():
    wildlife = db.execute("SELECT * FROM wildlife")

    wildlife_list = list()

    for park in wildlife:
        temp_dict = dict()
        temp_dict['name'] = park['name']
        temp_dict['image1'] = park['image1']
        temp_dict['image2'] = park['image2']
        wildlife_list.append(temp_dict)


    return render_template("index.html", wildlife_list=wildlife_list)

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


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # get time of transaction
        time = strftime("%Y-%m-%d %H:%M:%S")
        username = db.execute("SELECT username FROM users where id = :session",
                              session=session["user_id"])
        # check for correct usage
        if not request.form.get("symbol"):
            return apology("must enter symbol", 400)
        symbol = request.form.get("symbol")

        # lookup current stock price
        current_price = lookup(symbol)
        if not current_price:
            return apology(u"\uE058" + "Stock is not available", 400)

        # check for correct usage
        if request.form.get("shares").isdigit() == True:
            frequency = int(request.form.get("shares"))
        else:
            return apology("Must be an integer!", 400)

        if frequency < 1:
            return apology("must be positive", 400)

        # select cash from database
        cash = db.execute("SELECT cash FROM users WHERE id = :session",
                          session=session["user_id"])

        # calculate total cost incurred by user
        cost = frequency * current_price['price']

        # check if user has enough cash
        if cash[0]['cash'] < cost:
            return apology(u"\uE058" + "Insufficient funds", 400)

        # subtract cost from user
        change = cash[0]['cash'] - cost

        # update the users cash in database
        db.execute("UPDATE users SET cash = :cash WHERE id = :session",
                   session=session["user_id"], cash=change)
        db.execute("INSERT INTO purchases (id,username,symbol,price,frequency,cost,cash,time) VALUES (:id,:username,:symbol,:price,:frequency,:cost,:cash,:time)",
                   id=session["user_id"], username=username[0]['username'], symbol=symbol, price=current_price['price'], frequency=frequency, cost=cost, cash=change, time=time)

        # redirect to homepage
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # select user history from database
    stocks = db.execute("SELECT symbol,price,frequency,time FROM purchases WHERE id = :session",
                        session=session["user_id"])
    index = []

    # iterate through rows in database
    for stock in stocks:
        portfolio = dict()
        if stock['frequency'] > 0:
            portfolio["transaction"] = "BUY"
            portfolio['shares'] = stock['frequency']
        else:
            portfolio["transaction"] = "SELL"
            portfolio['shares'] = -stock['frequency']
        portfolio['stocks'] = stock['symbol']
        portfolio['price'] = stock['price']
        portfolio['time'] = stock['time']
        index.append(portfolio)

    # pass rows to html
    return render_template("history.html", index=index)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        # lookup current stock price
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology(u"\uE058" + "Stock is not available", 400)
        else:
            return render_template("quoted.html", name=quote['name'], price=usd(quote['price']), symbol=quote['symbol'])
    else:
        return render_template("quote.html")


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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        username = db.execute("SELECT username FROM users where id = :session",
                              session=session["user_id"])
        # record time of transaction
        time = strftime("%Y-%m-%d %H:%M:%S")

        # check for correct usage
        if not request.form.get("symbol"):
            return apology("must select stock", 400)
        bid = request.form.get("symbol")

        # lookup current stock price
        value = lookup(bid)

        # select cash from database
        balance = db.execute("SELECT cash FROM users WHERE id = :session",
                             session=session["user_id"])

        # check if user owns the stock
        stocks = db.execute("SELECT symbol, SUM(frequency) as total_shares FROM purchases WHERE id = :session AND symbol = :symbol GROUP BY symbol",
                            session=session["user_id"], symbol=bid)
        if not stocks:
            return apology("You do not own this stock", 400)

        shares = int(request.form.get("shares"))

        if shares < 1:
            return apology("must be positive", 400)

        # check if user has enough shares
        if stocks[0]['symbol'] == bid:
            if stocks[0]['total_shares'] < shares:
                return apology("Insufficient Shares", 400)
            else:

                # calculate new user value
                cash = balance[0]['cash'] + (shares * value['price'])

                # insert sale into database
                db.execute("INSERT INTO purchases (id,username,symbol,price,frequency,cost,cash,time) VALUES (:id,:username,:symbol,:price,:frequency,:cost,:cash,:time)",
                           id=session["user_id"], username=username[0]['username'], symbol=bid, price=value['price'], frequency=-shares, cost=-value['price'] * shares, cash=cash, time=time)

                # update user cash
                db.execute("UPDATE users SET cash = :cash WHERE id = :session",
                           session=session["user_id"], cash=cash)

        return redirect("/")

    else:
        stocks = db.execute("SELECT symbol, SUM(frequency) as total_shares FROM purchases WHERE id = :session GROUP BY symbol",
                            session=session["user_id"])
        owned_stocks = []

        # pass stocks user already owns to html
        for stock in stocks:
            if stock['total_shares'] > 0:
                owned_stocks.append(stock['symbol'])

        return render_template("sell.html", stocks=owned_stocks)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        if request.form.get("add").isdigit == False:
            return apology("must be a digit", 400)

        money = int(request.form.get("add"))
        if money < 0:
            return apology("Positive integers only", 400)

        # update user cash
        db.execute("UPDATE users SET cash = cash + :money WHERE id = :session",
                   session=session["user_id"], money=money)
        total_cash = db.execute("SELECT cash FROM users WHERE id = :session",
                                session=session['user_id'])

        # pass transaction to html
        return render_template("added.html", money=money, cash=total_cash[0]['cash'])
    else:
        return render_template("add.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

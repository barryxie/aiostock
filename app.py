from crypt import methods
from datetime import date
from flask import Flask,render_template,jsonify,redirect,request, session
from flask_debugtoolbar import DebugToolbarExtension
from models import Watchlist, db, connect_db, User, Watchlist
from form import EditUserForm, RegisterForm, LoginForm, addWatchlist
import websocket
import requests




Finnhub_BASE_URL = "https://finnhub.io/api/v1/"
Finnhub_Token = "c8634eiad3i9fvjhud4g"


Alphavantage_BASE_URL= "https://www.alphavantage.co/query?"
Alphavantage_Token = "TNW6QY7M5DYFUG44"

nasdaq_BASE_URL="https://data.nasdaq.com/api/v3/datasets/"
nasdaq_Token="bxSDX_Ky18soSMbfvdK3"


today = date.today()
day = today.strftime("%Y-%m-%d")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///aiostock'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'toosecret'
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS']= False

connect_db(app)

# db.drop_all()
# db.create_all()


 


def get_us_new(num):
    news_list = []
    res = requests.get(f"{Finnhub_BASE_URL}news?category=general&token={Finnhub_Token}")
    data = res.json()
    x = 0
    while x < num:
        news_list.append(data[x])
        x += 1
    return news_list



def get_company_news(symbol):
    res = requests.get(f"{Finnhub_BASE_URL}company-news?symbol={symbol}&from={day}&to={day}&token={Finnhub_Token}")
    news = res.json()
    return news



@app.route('/api/header')
def get_header_value():
    data = []
    tickers = ["SPY","QQQ","DIA","SQQQ"]
    for ticker in tickers:
        res = requests.get(f"{Finnhub_BASE_URL}quote?symbol={ticker}&token={Finnhub_Token}")
        res_json = res.json()
        quote = {"symbol":ticker, "data": res_json}
        data.append(quote)
    return jsonify(data)

@app.route('/api/<symbol>')
def get_symbol(symbol):
    res = requests.get(f"{Finnhub_BASE_URL}quote?symbol={symbol}&token={Finnhub_Token}")
    ticker = res.json()
    return jsonify(ticker)

@app.route('/api/users/<username>/watchlist')
def get_users_watchlist(username):
    watchlists = Watchlist.query.filter_by(username=username).all()
    ticker = watchlists.json()
    return jsonify(ticker)        



@app.route("/")
def get_home():
    news = get_us_new(4)
    return render_template('index.html', news=news)

@app.route("/search", methods=['POST'])
def get_search():
    symbol = request.form['search']
    return redirect(f'/{symbol}')

@app.route('/<symbol>')
def get_company_overview(symbol):
    res = requests.get(f'{Alphavantage_BASE_URL}function=OVERVIEW&symbol={symbol}&apikey={Alphavantage_Token}')
    # res = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo')
    company = res.json()
    news = get_company_news(symbol)

    data = requests.get(f"{Finnhub_BASE_URL}quote?symbol={symbol.upper()}&token={Finnhub_Token}")
    symbol_data = data.json()

    
    return render_template('symbol.html', company=company, news=news, ticker=symbol_data)

@app.route("/register" , methods=['GET', 'POST']) 
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        phone = form.phone.data
        first_name = ""
        last_name = ""

        user = User.register(username,password,email,phone, first_name, last_name)

        db.session.commit()
        session['username'] = user.username

        return redirect('/')
    else:
        return render_template('/users/register.html', form=form) 

@app.route("/login" , methods=['GET', 'POST']) 
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username,password)
        if user:
            session['username'] = user.username
            return redirect('/')
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template('users/login.html', form=form)    

    else:
        return render_template('users/login.html', form=form)         

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect('/') 

@app.route('/users/<username>')
def user_info(username):
    if "username" not in session:
        return redirect('/users/login.html') 

    else:
        user = User.query.get_or_404(username) 
        form = EditUserForm()
    return render_template("/users/info.html", user = user, form= form)  

@app.route('/users/<username>/watchlist',  methods=['GET', 'POST'])
def user_watchlist(username):
    if "username" not in session:
        return redirect('/users/login.html') 

    else:
        user = User.query.get_or_404(username) 
        form = addWatchlist()
        watchlists = Watchlist.query.filter_by(username=username).all()
        return render_template("/users/watchlist.html", user = user, form=form, watchlists=watchlists)

@app.route('/users/<username>/watchlist/add',  methods=['POST'])
def user_watchlist_add(username):
    if "username" not in session:
        return redirect('/users/login.html') 

    else:
        
        form = addWatchlist()
        form.validate_on_submit()
        symbol = form.symbol.data
        watchlist = Watchlist(username=username,symbol=symbol)

        db.session.add(watchlist)
        db.session.commit()
        return redirect(f"/users/{username}/watchlist")     
                



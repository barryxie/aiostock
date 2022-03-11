from crypt import methods
from datetime import date
from flask import Flask,render_template,jsonify,redirect,request, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import Watchlist, db, connect_db, User, Watchlist
from form import UpdatePasswordForm, RegisterForm, LoginForm, addWatchlist
import requests




Finnhub_BASE_URL = "https://finnhub.io/api/v1/"
Finnhub_Token = "c8634eiad3i9fvjhud4g"


Alphavantage_BASE_URL= "https://www.alphavantage.co/query?"
Alphavantage_Token = "TNW6QY7M5DYFUG44"




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




def get_header_value():
    data = []
    tickers = ["SPY","QQQ","DIA","SQQQ"]
    for ticker in tickers:
        res = requests.get(f"{Finnhub_BASE_URL}quote?symbol={ticker}&token={Finnhub_Token}")
        res_json = res.json()
        quote = {"symbol":ticker, "data": res_json}
        data.append(quote)
    return data

@app.route('/api/<symbol>')
def get_symbol(symbol):
    res = requests.get(f"{Finnhub_BASE_URL}quote?symbol={symbol}&token={Finnhub_Token}")
    ticker = res.json()
    return jsonify(ticker)
  



@app.route("/")
def get_home():
    news = get_us_new(4)
    cpi = requests.get("https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey=demo")
    cpi_data = cpi.json()
    gdp = requests.get("https://www.alphavantage.co/query?function=REAL_GDP&interval=annual&apikey=demo")
    gdp_data=gdp.json()
    yield10 = requests.get("https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=monthly&maturity=10year&apikey=demo")
    yield10_data=yield10.json()
    unemployment_rate = requests.get("https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey=demo")
    unemployment_rate_data=unemployment_rate.json()
    tickers =get_header_value()

    
    

    return render_template('index.html', news=news, cpi_data=cpi_data, gdp_data=gdp_data, yield10_data=yield10_data, unemployment_rate_data=unemployment_rate_data, tickers=tickers)

@app.route("/search", methods=['POST'])
def get_search():
    symbol = request.form['search']
    return redirect(f'/{symbol}')

@app.route('/<symbol>')
def get_company_overview(symbol):
    tickers =get_header_value()
    
    

    res = requests.get(f'{Alphavantage_BASE_URL}function=OVERVIEW&symbol={symbol}&apikey={Alphavantage_Token}')
    # res = requests.get('https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo')
    company = res.json()
    news = get_company_news(symbol)

    data = requests.get(f"{Finnhub_BASE_URL}quote?symbol={symbol.upper()}&token={Finnhub_Token}")
    symbol_data = data.json()

    if "username" in session:
        if Watchlist.query.filter_by(symbol=symbol.upper(),username=session["username"]).first():
            check_symbol = True
           
            return render_template('symbol.html', company=company, news=news, ticker=symbol_data,  tickers=tickers, check_symbol=check_symbol)
        else:
            check_symbol = False
            
            return render_template('symbol.html', company=company, news=news, ticker=symbol_data,  tickers=tickers, check_symbol=check_symbol)  
             
       
    else: 
        return render_template('symbol.html', company=company, news=news, ticker=symbol_data,  tickers=tickers)

@app.route('/<symbol>/income-statement') 
def get_income_statement(symbol):
    if "username" not in session:
        return redirect('/login') 
    else:
        res = requests.get(f'{Alphavantage_BASE_URL}function=INCOME_STATEMENT&symbol={symbol}&apikey={Alphavantage_Token}')
        statements = res.json()
        return render_template("incomestatement.html", statements=statements)
    


@app.route("/register" , methods=['GET', 'POST']) 
def register():
    tickers =get_header_value()
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        phone = form.phone.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username,password,email,phone, first_name, last_name)

        db.session.commit()
        session['username'] = user.username

        return redirect('/')
    else:
        return render_template('/users/register.html', form=form,  tickers=tickers) 

@app.route("/login" , methods=['GET', 'POST']) 
def login():
    tickers =get_header_value()
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
            return render_template('users/login.html', form=form, tickers=tickers)    

    else:
        return render_template('users/login.html', form=form, tickers=tickers)         

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect('/') 

@app.route('/users/<username>/')
def user_info(username):
    tickers =get_header_value()
    if "username" not in session:
        return redirect('/login') 

    else:
        user = User.query.get_or_404(username) 
        form = UpdatePasswordForm()
        return render_template("/users/info.html", user = user, form= form, tickers=tickers)         


@app.route('/users/<username>/updatepassword', methods=['POST'])
def update_password(username):
    tickers =get_header_value()
    if "username" not in session:
        return redirect('/login') 

    else:
        user = User.query.get_or_404(username) 
        form = UpdatePasswordForm()
        if form.validate_on_submit():
            username = session['username']
            password = form.password.data
            user = User.authenticate(username,password)
            if user:
                new_password = form.new_password.data
                confirm_password = form.confirm_password.data
                if new_password == confirm_password:
                    newpassword = User.newpassword(new_password)
                    user.password = newpassword
                    db.session.commit()
                    flash('Password updated')
                    return redirect(f'/users/{username}')
                else:
                    flash('Password not match') 
                    return redirect(f'/users/{username}')  
            else:
                flash("incorrent password, please try again")  
                return redirect(f'/users/{username}')       


     

@app.route('/users/<username>/watchlist')
def user_watchlist(username):
    
    
    tickers =get_header_value()
    if "username" not in session:
        return redirect('/login') 

    else:
        
       
        user = User.query.get_or_404(username) 
        form = addWatchlist()
        watchlists = Watchlist.query.filter_by(username=username).all()

        data = []
        for watchlist in watchlists:
            res = requests.get(f"{Finnhub_BASE_URL}quote?symbol={watchlist.symbol}&token={Finnhub_Token}")
            res_json = res.json()
            quote = {"symbol":watchlist.symbol,"id":watchlist.id, "data": res_json}
            data.append(quote)
          
        return render_template("/users/watchlist.html", user = user, form=form, watchlists=watchlists, data=data, tickers=tickers)

@app.route('/users/<username>/watchlist/add',  methods=['POST'])
def user_watchlist_add(username):
    if "username" not in session or username != session["username"]:
        return redirect('/login') 

    else:
        
        form = addWatchlist()
        form.validate_on_submit()
        symbol = form.symbol.data
        if Watchlist.query.filter_by(symbol=symbol,username=username).first():
            flash("symbol already in your watchlist")
            return redirect(f"/users/{username}/watchlist") 
        else:
            watchlist = Watchlist(username=username,symbol=symbol.upper() )

            db.session.add(watchlist)
            db.session.commit()
            flash("Symbol has added")
            return redirect(f"/users/{username}/watchlist")  
            
                 

@app.route('/users/<username>/watchlist/<symbol>/add',  methods=['POST'])
def user_watchlist_overview_add(username, symbol):
    if "username" not in session or username != session["username"]:
        return redirect('/login') 

    else:
        watchlist = Watchlist(username=username,symbol=symbol.upper() )
        db.session.add(watchlist)
        db.session.commit()
        return redirect(f"/{symbol}")                 

@app.route('/users/<username>/watchlist/<symbol>/delete',  methods=['POST'])
def user_watchlist_overview_delete(username, symbol):
    if "username" not in session or username != session["username"]:
        return redirect('/login') 

    else:
        watchlist = Watchlist.query.filter_by(symbol=symbol.upper(),username=session["username"]).first()
        
        db.session.delete(watchlist)
        db.session.commit()
        return redirect(f"/{symbol}")   
        

@app.route('/users/<username>/watchlist/<int:id>/delete',  methods=['POST'])
def user_watchlist_delete(username, id):
    if "username" not in session or username != session["username"]:
        return redirect('/login') 

    else:
        watchlist = Watchlist.query.filter_by(id=id).first()
        
        db.session.delete(watchlist)
        db.session.commit()
             
        return redirect(f"/users/{username}/watchlist")              
                                         
                



from app import app
from flask import render_template,redirect,request,session,flash
from app.models.user import User
from app.models.game import Game
from app.models.price import Price
from app.models.review import Review
from flask_bcrypt import Bcrypt
import random
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    all_prices = Price.get_prices_filtered()
    all_free = Price.get_prices_free()
    random_prices = random.sample(all_prices, 6)
    most_expensive = Price.get_six_most_expensive()
    top_games = Review.get_top_five_games()
    top_games.sort(key=lambda game: Review.get_average_review(game['game_id']), reverse=True)
    top_5_games = top_games[:5]
    return render_template("index.html", random_prices=random_prices, all_free=all_free, most_expensive=most_expensive, top_5_games=top_5_games)

@app.route("/register" , methods = ['POST'])
def register():

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)

    data = {
        "name" : request.form["name"],
        "email" : request.form["email"],
        "password" : pw_hash,
        "c_password" : request.form["c_password"],
    }
    if not all(request.form.values()):
        flash("One or more fields empty, check the form again.")
        return redirect(request.referrer)
    if not User.validate_user(request.form):
        return redirect('/registrar')
    User.save_user(data)
    return redirect ('/acceder')

@app.route("/acceder")
def logintemplate():
    return render_template("login.html")

@app.route("/registrar")
def registertemplate():
    return render_template("register.html")

@app.route("/login" , methods = ['POST'])
def login():
    data = { 
        "email" : request.form["email"],
        "password" : request.form["password"]
        }
    
    user_in_db = User.get_by_email(data)

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)

    if not user_in_db:
        flash("Correo o contraseña invalidos")
        return redirect("/acceder")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Correo o contraseña invalidos")
        return redirect('/acceder')
    
    session['user_id'] = user_in_db.id
    print(user_in_db.id)

    return redirect("/")

@app.route('/logout' , methods = ['POST'])
def logout():
    session.clear()
    return redirect('/')
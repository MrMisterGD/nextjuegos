from app import app
from flask import render_template,redirect,request,session,flash,jsonify
from app.models.game import Game
from app.models.price import Price
from app.models.review import Review
import random



@app.route("/juego/<game>")
def gametemplate(game):
    data = {
        "name": game,
    }
    game_info = Game.get_one_game(data)
    price_info = Price.get_prices(data)
    all_prices = Price.get_prices_filtered()
    random_prices = random.sample(all_prices, 6)
    average_review = Review.get_average_review(game_info.id)

    return render_template("game.html", game_info=game_info, price_info=price_info, random_prices=random_prices, average_review=average_review)

@app.route('/search/<term>', methods=['GET'])
def search(term):
    term = request.args.get('term', '')
    games = Game.search(term)
    return render_template('search.html', games=games)

@app.route('/search/')
def searchtemplate():
    return redirect('/')

@app.route('/vote/<game>', methods=['POST'])
def review(game):
    data = {
        'grade': request.form['star']

    }
    game_data = {
        'name': game
    }
    game_obj = Game.get_one_game(game_data)
    if game_obj:
        data['game_id'] = game_obj.id
        user_id = session.get('user_id')
        if user_id:
            existing_review = Review.get_review_by_user_and_game(user_id, game_obj.id)
            if existing_review:
                flash('You have already reviewed this game.', 'error')
                return redirect(f'/juego/{game}')

            # Save review to database
            data['user_id'] = user_id
            Review.save_review(data)
        else:
            flash('You must be logged in to leave a review.', 'error')
            return redirect('/registrar')


    else:
        flash("Game not found", 'error')
    return redirect(f'/juego/{game}')
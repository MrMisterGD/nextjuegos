from app.config.mysqlconnection import connectToMySQL
from app import app
from flask import flash, request, session

class Price:
    def __init__( self , data ):
        self.id = data['id']
        self.shop_id = data['shop_id']
        self.game_id = data['game_id']
        self.price = data['price']
        self.discount = data['discount']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_prices(cls, data):
        name = data['name'].replace('_', ' ')
        query = "SELECT s.name AS shop_name, g.name AS name, g.image AS image, p.price, p.discount FROM prices p JOIN shops s ON p.shop_id = s.id JOIN games g ON p.game_id = g.id WHERE g.name = %(name)s ORDER BY s.name, g.name;"
        return connectToMySQL('gamedb').query_db(query, {'name': name})
    
    @classmethod
    def get_prices_filtered(cls):
        query = "SELECT s.name AS shop_name, g.name AS name, g.image AS image, p.price, p.discount FROM prices p JOIN shops s ON p.shop_id = s.id JOIN games g ON p.game_id = g.id WHERE price >= 20000 and discount >= 50 ORDER BY s.name, g.name;"
        return connectToMySQL('gamedb').query_db(query)
    
    @classmethod
    def get_prices_free(cls):
        query = "SELECT s.name AS shop_name, g.name AS name, g.image AS image, p.price, p.discount FROM prices p JOIN shops s ON p.shop_id = s.id JOIN games g ON p.game_id = g.id WHERE discount = 100 ORDER BY s.name, g.name;"
        return connectToMySQL('gamedb').query_db(query)
    
    @classmethod
    def get_six_most_expensive(cls):
        query = "SELECT s.name AS shop_name, g.name AS name, g.image AS image, p.price, p.discount FROM prices p JOIN shops s ON p.shop_id = s.id JOIN games g ON p.game_id = g.id WHERE p.price > 90000 ORDER BY p.price DESC LIMIT 6;"
        return connectToMySQL('gamedb').query_db(query)

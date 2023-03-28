from app.config.mysqlconnection import connectToMySQL
from app import app
from flask import flash, request, session
import pymysql

class Game:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.image = data['image']
        self.req_min = data['req_min']
        self.req_max = data['req_max']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_all_games(cls):
        query = "SELECT * FROM games;"
        return connectToMySQL('gamedb').query_db(query, {'id': session['user_id']})
    
    @classmethod
    def get_one_game(cls, data):
        name = data['name'].replace('_', ' ')
        query = "SELECT * FROM games WHERE name = %(name)s;"
        result = connectToMySQL('gamedb').query_db(query, {'name': name})
        if result:
            return cls(result[0])
        else:
            return None

    @classmethod
    def search(cls, term):
        query = "SELECT * FROM games WHERE name LIKE %s"
        conn = pymysql.connect(host = 'localhost',
                                    user = 'root',
                                    password = 'root', 
                                    db = 'gamedb',
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
        cur = conn.cursor()
        cur.execute(query, ('%' + term + '%',))
        result_set = cur.fetchall()
        return result_set
from app.config.mysqlconnection import connectToMySQL
from app import app
from flask import flash, request, session

class Review:
    def __init__( self , data ):
        self.id = data['id']
        self.game_id = data['user_id']
        self.game_id = data['game_id']
        self.grade = data['grade']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save_review(cls, data):
        user_id = session.get('user_id')
        if user_id:
            data['user_id'] = user_id
            query = "INSERT INTO reviews (user_id, game_id, grade, created_at, updated_at) VALUES (%(user_id)s, %(game_id)s, %(grade)s, NOW(), NOW());"
            return connectToMySQL('gamedb').query_db(query, data)
        else:
            flash('You must be logged in to leave a review.', 'error')
            return None
        
    @classmethod
    def get_review_by_user_and_game(cls, user_id, game_id):
        query = "SELECT * FROM reviews WHERE user_id = %(user_id)s AND game_id = %(game_id)s"
        data = {
            'user_id': user_id,
            'game_id': game_id
        }
        result = connectToMySQL('gamedb').query_db(query, data)
        if result:
            return cls(result[0])
        return None
    
    @classmethod
    def get_average_review(cls, game_id):
        query = "SELECT AVG(grade) as average_grade FROM reviews WHERE game_id = %(game_id)s"
        data = {'game_id': game_id}
        result = connectToMySQL('gamedb').query_db(query, data)
        if result[0]['average_grade'] is not None:
            return round(result[0]['average_grade'], 1)
        else:
            return 0
        
    @classmethod
    def get_top_five_games(cls):
        query = """
            SELECT g.id AS game_id, g.name AS name, g.image AS image, AVG(r.grade) AS average_grade, COUNT(r.game_id) AS review_count
            FROM games AS g
            INNER JOIN reviews AS r ON g.id = r.game_id
            GROUP BY g.id
            ORDER BY average_grade DESC, review_count DESC
            LIMIT 50
        """
        result = connectToMySQL('gamedb').query_db(query)
        sorted_games = sorted(result, key=lambda game: game['average_grade'], reverse=True)[:5]
        return sorted_games
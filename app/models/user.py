from app.config.mysqlconnection import connectToMySQL
from app import app
from flask import flash, request, session
import re
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
class User:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @staticmethod
    def validate_user(user):
        is_valid = True
        if len(user['name']) < 2:
            flash("Name must be at least 2 characters.")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False
        query = "SELECT * FROM users WHERE email = %(email)s;"
        data = { 'email': user['email'] }
        result = connectToMySQL('gamedb').query_db(query, data)
        if result:
            flash("Email address already in use.")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters.")
            is_valid = False
        if user['password'] != user['c_password']:
            flash("Password fields appear to be different, check your spelling.")
            is_valid = False
        return is_valid
        
    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL("gamedb").query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def get_one_user(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        result = connectToMySQL('gamedb').query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return None
    
    @classmethod
    def save_user( cls, data ):
        query = "INSERT INTO users ( name , email , password , created_at, updated_at ) VALUES ( %(name)s  , %(email)s , %(password)s , NOW() , NOW() );"
        return connectToMySQL('gamedb').query_db( query, data )
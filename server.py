from app import app, render_template, request, redirect
from app.controllers import users, games

if __name__ == "__main__":
    app.run(debug=True)
from bs4 import BeautifulSoup
import requests
from app.config.mysqlconnection import connectToMySQL

db = connectToMySQL('gamedb')

url = "https://store.epicgames.com/es-ES/browse?sortBy=releaseDate&sortDir=DESC&count=100&start=0"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

total_pages = soup.find("nav", attrs={"data-testid": "egs-pagination"})
max_num_pages = 3

game_data = []
game_names = set() # create a set to store the game names

# Iterate through all the pages
page_num = 0
while page_num <= max_num_pages * 100:
    url = f"https://store.epicgames.com/es-ES/browse?sortBy=releaseDate&sortDir=DESC&count=100&start={page_num}"
    print(f"Scraping games from {page_num} to {page_num + 100}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    page_num += 100

    if soup.find("nav", {"data-testid": "egs-pagination"}) is None:
        break

    img_tags = soup.find_all("nav", {"data-testid": "egs-pagination"})
    for img_tag in img_tags:
        game_result = img_tag.find_parent("a")
        game_name = game_result.find("div", {"class": "css-rgqwpc"}).text.strip()
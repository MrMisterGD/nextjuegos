from bs4 import BeautifulSoup
import requests
from app.config.mysqlconnection import connectToMySQL
import re

db = connectToMySQL('gamedb')

url = "https://store.steampowered.com/search/?category1=998" # The first page of video games
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

total_pages = soup.find("div", {"class": "search_pagination_right"}).find_all("a")[-2].text # Get the total number of pages
game_data = []
game_names = set() # create a set to store the game names
max_num_pages = 10000  # Set a large maximum number of pages to scrape


# Iterate through all the pages
for page_num in range(1, max_num_pages + 1):
    url = f"https://store.steampowered.com/search/?category1=998&page={page_num}"
    print(f"Scraping page {page_num}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find("div", {"class": "search_pagination_right"}) is None:
        break

    # Get the game names and prices for the current page
    img_tags = soup.find_all("div", {"class": "search_capsule"})
    for img_tag in img_tags:
        game_result = img_tag.find_parent("a")
        game_name = game_result.find("span", {"class": "title"}).text.strip()

    # Check if the game name already exists in the set
        if game_name not in game_names:
            price_container = game_result.find("div", {"class": "col search_price_discount_combined responsive_secondrow"})
            if not price_container:
                price_container = game_result.find("div", {"class": "col search_price responsive_secondrow"})

            original_price_element = price_container.find("strike")
            if original_price_element:
                original_price = original_price_element.text.strip()
                final_price = price_container.find("div").text.strip()
                discount_element = price_container.find("div", {"class": "search_discount"})
                discount = discount_element.text.strip() if discount_element else "0"
            else:
                original_price = price_container.find("div", {"class": "search_price"}).text.strip()
                final_price = original_price
                discount = "0"

            
            img = img_tag.find("img")
            img_url = img["src"] if img else ""

            # Add the game name to the set
            game_names.add(game_name)
            game_data.append((game_name, original_price, final_price, discount, img_url))

# Save the game data to MySQL database
print("Saving data to MySQL database...")
for data in game_data:
    print(data)
    # Insert the game name into the games table, escaping any apostrophes in the name
    game_name = data[0].replace("'", "''")
    game_name = data[0].replace("%", "%%")
    game_name = re.sub(r'[^\x00-\x7F]+', '', game_name)
    game_sql = "INSERT INTO games (name, image, created_at, updated_at) SELECT %(name)s, %(image)s, NOW(), NOW() FROM dual WHERE NOT EXISTS (SELECT * FROM games WHERE name = %(name)s)"
    game_val = {'name': game_name, 'image' : data[4]}
    db.query_db(game_sql, game_val)
    game_id_sql = "SELECT id FROM games WHERE name = %(name)s"
    game_id_val = {'name': game_name}
    game_id = db.query_db(game_id_sql, game_id_val)
    if game_id == None:
        continue
    game_id = game_id[0]['id']

    # Remove any non-digit characters from the price and discount strings
    price = re.sub(r'\D', '', data[1])
    discount = re.sub(r'\D', '', data[3]) if data[3] else "0"
    discount.replace("''", "")

    price_sql = "SELECT * FROM prices WHERE shop_id = %(shop_id)s AND game_id = %(game_id)s"
    price_val = {'shop_id': 1, 'game_id': game_id}
    price_record = db.query_db(price_sql, price_val)

    if price_record:
        # If a record exists, update the price and discount for that record
        update_sql = "UPDATE prices SET price = %(price)s, discount = %(discount)s, updated_at = NOW() WHERE id = %(id)s"
        update_val = {'price': price, 'discount': discount, 'id': price_record[0]['id']}
        db.query_db(update_sql, update_val)

    # Insert the price and discount into the prices table, linked to the corresponding game ID
    else:
        price_sql = "INSERT INTO prices (shop_id, game_id, price, discount, created_at, updated_at) VALUES (1, %(game_id)s, %(price)s, %(discount)s, NOW(), NOW())"
        price_val = {'game_id': game_id, 'price': price, 'discount': discount}
        if discount == "N/A":
            price_val['discount'] = 0
        else:
            if price_val['discount'] == '':
                price_val['discount'] = 0
            if price_val['price'] == '':
                price_val['price'] = 0
        db.query_db(price_sql, price_val)

print("Done!")
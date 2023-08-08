from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
import csv
import os

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/gallery')
def gallery():
    recipes = fetch_recipes()
    for recipe in recipes:
        ratings = [int(rating) for rating in recipe["user_ratings"].split(",") if rating]
        recipe["average_rating"] = sum(ratings) / len(ratings) if ratings else "No ratings yet"
    return render_template('gallery.html', recipes=recipes)



@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        # For now, we'll use a placeholder image link. Later, we'll handle actual image uploads.
        recipe_data = {
            "recipe_name": request.form.get("recipe_name"),
            "image_link": "images/recipe_placeholder.jpg",
            "ingredients": request.form.get("ingredients"),
            "preparation": request.form.get("preparation"),
            "serving": request.form.get("serving"),
            "user_ratings": ""  # initially empty
        }
        save_recipe(recipe_data)
        return redirect(url_for('gallery'))
    return render_template('submit.html')



@app.route('/manage')
def manage():
    recipes = fetch_recipes()
    return render_template('manage.html', recipes=recipes)



@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('search_term')
    ingredient_filter = request.args.get('ingredient_filter')
    recipes = search_recipes(search_term, ingredient_filter)
    return render_template('search.html', recipes=recipes, search_term=search_term, ingredient_filter=ingredient_filter)

@app.route('/rate_recipe', methods=['POST'])
def rate_recipe():
    recipe_name = request.form.get("recipe_name")
    rating = request.form.get("rating")
    if recipe_name and rating:
        update_ratings(recipe_name, rating)
    return redirect(url_for('gallery'))  # Redirect back to gallery after rating


@app.route('/delete_recipe/<recipe_name>', methods=['POST'])
def delete_recipe(recipe_name):
    recipes = fetch_recipes()
    recipes = [recipe for recipe in recipes if recipe['recipe_name'] != recipe_name]

    # Save the updated recipes back to the CSV
    with open(os.path.join("csvfiles", "recipes.csv"), "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["recipe_name", "image_link", "ingredients", "preparation", "serving",
                                                  "user_ratings"])
        writer.writeheader()
        for recipe in recipes:
            writer.writerow(recipe)

    return redirect(url_for('manage'))


def fetch_recipes():
    recipes = []
    with open(os.path.join("csvfiles", "recipes.csv"), "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipes.append(row)
    return recipes

def save_recipe(recipe_data):
    with open(os.path.join("csvfiles", "recipes.csv"), "a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["recipe_name", "image_link", "ingredients", "preparation", "serving", "user_ratings"])
        writer.writerow(recipe_data)


def search_recipes(search_term=None, ingredient_filter=None):
    recipes = fetch_recipes()
    filtered_recipes = []

    for recipe in recipes:
        if search_term and search_term.lower() not in recipe['recipe_name'].lower():
            continue
        if ingredient_filter and ingredient_filter.lower() not in recipe['ingredients'].lower():
            continue
        filtered_recipes.append(recipe)

    return filtered_recipes


def get_ratings(recipe_name):
    recipes = fetch_recipes()
    for recipe in recipes:
        if recipe["recipe_name"] == recipe_name:
            return [int(rating) for rating in recipe["user_ratings"].split(",") if rating]
    return []


def update_ratings(recipe_name, new_rating):
    recipes = fetch_recipes()
    updated = False

    # Find the recipe and update its ratings
    for recipe in recipes:
        if recipe["recipe_name"] == recipe_name:
            current_ratings = recipe["user_ratings"].split(",")
            current_ratings.append(str(new_rating))
            recipe["user_ratings"] = ",".join(current_ratings)
            updated = True
            break

    # If we updated the ratings, save back to the CSV
    if updated:
        with open(os.path.join("csvfiles", "recipes.csv"), "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["recipe_name", "image_link", "ingredients", "preparation", "serving", "user_ratings"])
            writer.writeheader()
            for recipe in recipes:
                writer.writerow(recipe)



if __name__ == '__main__':
    app.run(debug=True)

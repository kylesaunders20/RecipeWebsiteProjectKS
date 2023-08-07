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
    return render_template('manage.html')


@app.route('/search', methods=['GET'])
def search():
    # We'll handle the search logic later.
    # For now, just render the search page.
    return render_template('search.html')

def fetch_recipes():
    recipes = []
    with open(os.path.join("data", "recipes.csv"), "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            recipes.append(row)
    return recipes

def save_recipe(recipe_data):
    with open(os.path.join("data", "recipes.csv"), "a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["recipe_name", "image_link", "ingredients", "preparation", "serving", "user_ratings"])
        writer.writerow(recipe_data)


if __name__ == '__main__':
    app.run(debug=True)

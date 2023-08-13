from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
import csv
import os

from werkzeug.utils import secure_filename

app = Flask(__name__)
Bootstrap(app)

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # Fetch all recipes
    recipes = fetch_recipes()

    for recipe in recipes:
        ratings = [int(rating) for rating in recipe["user_ratings"].split(",") if rating]
        recipe["average_rating"] = sum(ratings) / len(ratings) if ratings else "No ratings yet"

    featured_recipes = recipes[:3]

    return render_template('index.html', featured_recipes=featured_recipes)



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
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            recipe_data = {
                "recipe_name": request.form.get("recipe_name"),
                "image_link": 'images/' + filename,  # Update the image link to point to the uploaded file
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
    search_term = request.args.get('search_term', '')
    ingredient_filter = request.args.get('ingredient_filter', '')
    recipes = search_recipes(search_term, ingredient_filter)

    for recipe in recipes:
        ratings = [int(rating) for rating in recipe["user_ratings"].split(",") if rating]
        recipe["average_rating"] = sum(ratings) / len(ratings) if ratings else "No ratings yet"

    return render_template('search.html', recipes=recipes, search_term=search_term, ingredient_filter=ingredient_filter)


@app.route('/rate_recipe', methods=['POST'])
def rate_recipe():
    recipe_name = request.form.get("recipe_name")
    rating = request.form.get("rating")
    if recipe_name and rating:
        update_ratings(recipe_name, rating)
        ratings = get_ratings(recipe_name)
        average_rating = round(sum(ratings) / len(ratings), 1) if ratings else "No ratings yet"
        return jsonify(success=True, average_rating=average_rating)
    return jsonify(success=False, message="Failed to rate the recipe.")



@app.route('/delete_recipe/<recipe_name>', methods=['POST'])
def delete_recipe(recipe_name):
    recipes = fetch_recipes()
    image_link_to_delete = None
    for recipe in recipes:
        if recipe['recipe_name'] == recipe_name:
            image_link_to_delete = recipe['image_link']
            break
    recipes = [recipe for recipe in recipes if recipe['recipe_name'] != recipe_name]

    # Save the updated recipes back to the CSV
    with open(os.path.join("csvfiles", "recipes.csv"), "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["recipe_name", "image_link", "ingredients", "preparation", "serving",
                                                  "user_ratings"])
        writer.writeheader()
        for recipe in recipes:
            writer.writerow(recipe)
    if image_link_to_delete:
        try:
            os.remove(os.path.join("static", image_link_to_delete))
        except OSError as e:
            print(f"Error deleting {image_link_to_delete}: {e}")

    return redirect(url_for('manage'))

@app.route('/recipe/<recipe_name>')
def recipe_detail(recipe_name):
    recipes = fetch_recipes()
    for recipe in recipes:
        if recipe["recipe_name"] == recipe_name:
            return render_template('recipe_detail.html', recipe=recipe)
    return "Recipe not found", 404



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            print(f"Updated ratings for {recipe_name}: {recipe['user_ratings']}")
            break

    # If we updated the ratings, save back to the CSV
    if updated:
        with open(os.path.join("csvfiles", "recipes.csv"), "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["recipe_name", "image_link", "ingredients", "preparation", "serving", "user_ratings"])
            writer.writeheader()
            for recipe in recipes:
                writer.writerow(recipe)

        # Print the recipes after the update
        print(f"Recipes after update: {recipes}")
    else:
        print(f"Recipe {recipe_name} not found in the list. No updates made.")




if __name__ == '__main__':
    app.run(debug=True)

import aiohttp
import asyncio
import json
import pandas as pd
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import settings

async def download_json(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            text = await response.text()
            with open(filename, 'w') as f:
                f.write(text)

def read_recipes(filename):
    recipes = []
    with open(filename) as f:
        for line in f:
            try:
                recipe = json.loads(line)
                recipes.append(recipe)
            except json.JSONDecodeError:
                print(f"Failed to parse: {line}")
    return recipes

def generate_misspellings():
    return {
        "chillies": ["chillies", "chilles", "chilies", "chiles", "chili", "chilli", "chilie", "chille"]
    }

def contains_chillies(ingredients, misspellings):
    misspellings_set = set(misspellings)
    for ingredient in ingredients:
        words = set(ingredient.lower().split())
        if misspellings_set.intersection(words):
            return True
    return False

def filter_chillies_recipes(recipes, misspellings):
    chilies_recipes = []
    for recipe in recipes:
        ingredients_str = recipe.get("ingredients", "")
        ingredients = ingredients_str.split('\n')
        if contains_chillies(ingredients, misspellings["chillies"]):
            prep_time_str = recipe.get('prepTime', '')
            cook_time_str = recipe.get('cookTime', '')
            prep_time = parse_time(prep_time_str)
            cook_time = parse_time(cook_time_str)
            total_time = prep_time + cook_time
            difficulty = determine_difficulty(total_time)
            recipe['prepTime'] = prep_time
            recipe['cookTime'] = cook_time
            recipe['difficulty'] = difficulty
            chilies_recipes.append(recipe)
    return chilies_recipes


def parse_time(time_str):
    if isinstance(time_str, int):
        return time_str
    if not isinstance(time_str, str):
        return 0
    hours = 0
    minutes = 0
    if 'H' in time_str or 'M' in time_str:
        if 'H' in time_str:
            hours = int(time_str.split('H')[0].replace('PT', ''))
            time_str = time_str.split('H')[1]
        if 'M' in time_str:
            minutes = int(time_str.split('M')[0].replace('PT', ''))
        return hours * 60 + minutes
    return 0

def determine_difficulty(total_time):
    if total_time > 60:
        return "Hard"
    elif 30 <= total_time <= 60:
        return "Medium"
    elif total_time < 30 and total_time != 0:
        return "Easy"
    return "Unknown"

def save_chilies_recipes(chilies_recipes, filename='Chilies.csv'):
    chilies_df = pd.DataFrame(chilies_recipes).drop_duplicates()
    chilies_df.to_csv(filename, sep="|", index=False)

def save_difficulty_aggregates(chilies_recipes, results_filename='Results.csv'):
    
    chilies_df = pd.DataFrame(chilies_recipes)

    chilies_df = chilies_df[chilies_df['difficulty'] != 'Unknown']

    chilies_df['prepTime'] = pd.to_numeric(chilies_df['prepTime'], errors='coerce')
    chilies_df['cookTime'] = pd.to_numeric(chilies_df['cookTime'], errors='coerce')

    difficulty_agg = chilies_df.groupby('difficulty').agg({'prepTime': 'mean', 'cookTime': 'mean'})

    difficulty_agg['AverageTotalTime'] = difficulty_agg['prepTime'] + difficulty_agg['cookTime']

    results = difficulty_agg.reset_index()[['difficulty', 'AverageTotalTime']]
    results.columns = ['Difficulty', 'AverageTotalTime']

    results_str = results.apply(lambda x: f"{x['Difficulty']}|AverageTotalTime|{x['AverageTotalTime']}", axis=1)

    with open(results_filename, 'w') as f:
        for line in results_str:
            f.write(f"{line}\n")


def process_recipes(json_filename):
    recipes = read_recipes(json_filename)
    misspellings = generate_misspellings()
    chilies_recipes = filter_chillies_recipes(recipes, misspellings)
    save_chilies_recipes(chilies_recipes)
    save_difficulty_aggregates(chilies_recipes)

async def main():
    url = settings.URL_RECIPES
    json_filename = os.path.join(os.pardir, "bi_recipes.json")
    await download_json(url, json_filename)
    process_recipes(json_filename)

if __name__ == "__main__":
    asyncio.run(main())
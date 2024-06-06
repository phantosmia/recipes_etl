import pytest
import os
import pandas as pd
import sys
from pathlib import Path

# Ensure the hf_bi_python_excercise directory is in the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hf_bi_python_excercise.main import generate_misspellings, parse_time, filter_chillies_recipes, save_chilies_recipes, save_difficulty_aggregates

# Test data
test_data = [
    {
        "name": "Recipe 1",
        "ingredients": "Chilies\nTomatoes",
        "prepTime": "PT20M",
        "cookTime": "PT40M"
    },
    {
        "name": "Recipe 2",
        "ingredients": "Tomatoes\nOnions",
        "prepTime": "PT10M",
        "cookTime": "PT15M"
    },
    {
        "name": "Recipe 3",
        "ingredients": "Chiles\nGarlic",
        "prepTime": "PT1H",
        "cookTime": "PT30M"
    },
]

@pytest.fixture
def recipes():
    return test_data

def test_generate_misspellings():
    misspellings = generate_misspellings()
    expected = ["chillies", "chilles", "chilies", "chiles", "chili", "chilli", "chilie", "chille", "chille", "chile"]
    assert misspellings["chillies"] == expected

def test_parse_time():
    assert parse_time("PT1H30M") == 90
    assert parse_time("PT45M") == 45
    assert parse_time("PT2H") == 120
    assert parse_time("") == 0

def test_filter_chillies_recipes(recipes):
    misspellings = generate_misspellings()
    chilies_recipes = filter_chillies_recipes(recipes, misspellings)
    assert len(chilies_recipes) == 2
    assert chilies_recipes[0]["name"] == "Recipe 1"
    assert chilies_recipes[1]["name"] == "Recipe 3"

def test_save_chillies_recipes(recipes):
    misspellings = generate_misspellings()
    chilies_recipes = filter_chillies_recipes(recipes, misspellings)
    save_chilies_recipes(chilies_recipes, filename='ChiliesTest.csv')
    assert os.path.exists('ChiliesTest.csv')
    df = pd.read_csv('ChiliesTest.csv', sep='|')
    assert len(df) == 2

def test_save_difficulty_aggregates(recipes):
    misspellings = generate_misspellings()
    chilies_recipes = filter_chillies_recipes(recipes, misspellings)
    save_difficulty_aggregates(chilies_recipes, results_filename='ResultsTest.csv')
    assert os.path.exists('ResultsTest.csv')
    df = pd.read_csv('ResultsTest.csv', sep='|', header=None)
    assert len(df) == 2

#!/usr/bin/env python3

# Pokécolours

from flask import Flask
from flask import request
from flask import Response

app = Flask(__name__)

import requests

POKEMON_API_URL = 'https://pokeapi.co/api/v2/'

COLOUR_URL = POKEMON_API_URL + 'pokemon-color'


def get_pokemon_by_colour(colour):
    # list species matching colour
    colour_json = requests.get(f'{COLOUR_URL}/{colour}').json()
    pokemon_species_list = colour_json['pokemon_species']

    for pokemon_species_link in pokemon_species_list:
        print(pokemon_species_link['name'])

        # GET information about a species
        pokemon_species_json = requests.get(pokemon_species_link['url']).json()


        # since a species may have multiple varieties
        # GET each variety
        varieties = pokemon_species_json['varieties']
        for variety in varieties:
            # (a variety is a pokemon)
            # GET the pokemon information
            pokemon_json = requests.get(variety['pokemon']['url']).json()

            pokemon_name = pokemon_json['name']
            image_url = pokemon_json['sprites']['front_default']
            
            
            html = f'<img src="{image_url}" alt="{pokemon_name}">{pokemon_name}<br><br>'

            yield html

# Order of routes is important

# This one will match if a colour is given
@app.route('/<colour>')
def get_by_colour(colour):

    return Response(get_pokemon_by_colour(colour))
    #return render_template("index.html")

# This one will match otherwise
@app.route('/')
def index():

    colours_json = requests.get(COLOUR_URL).json()
    colours_list = colours_json['results']

    html = ''
    for colour in colours_list:
        url = '/' + colour['name']
        html += f'<a href="{url}">{colour["name"]}</a><br>'
    
    return html

#!/usr/bin/env python3

# Pokécolours

from flask import Flask
from flask import request # work with the current Flask request
from flask import Response

app = Flask(__name__)

import requests # <-- can do requests to an API

POKEMON_API_URL = 'https://pokeapi.co/api/v2/'

COLOUR_URL = POKEMON_API_URL + 'pokemon-color'


class PokemonApiCache:
    def __init__(self):
        self.request_history = {}

    def get(self, url):
        """Generically requests a generic URL and caches result"""
        
        # have we already made this request before
        if url in self.request_history:
            previous_result = self.request_history[url]
            return previous_result

        # no we haven't so do it
        result = requests.get(url).json() # <-- this does not give you JSON
                                          # actually it treats the response as JSON
                                          # but parses it into a Python dict thing
        # cache the result
        self.request_history[url] = result

        return result

request_cache = PokemonApiCache()


def get_pokemon_by_colour(colour):
    # list species matching colour
    colour_json = request_cache.get(f'{COLOUR_URL}/{colour}')
    pokemon_species_list = colour_json['pokemon_species']

    for pokemon_species_link in pokemon_species_list:
        print(pokemon_species_link['name'])

        # GET information about a species
        pokemon_species_json = request_cache.get(pokemon_species_link['url'])


        # since a species may have multiple varieties
        # GET each variety
        varieties = pokemon_species_json['varieties']
        for variety in varieties:
            # (a variety is a pokemon)
            # GET the pokemon information
            pokemon_json = request_cache.get(variety['pokemon']['url'])

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

    colours_json = request_cache.get(COLOUR_URL)
    colours_list = colours_json['results']

    html = ''
    for colour in colours_list:
        url = '/' + colour['name']
        html += f'<a href="{url}">{colour["name"]}</a><br>'
    
    return html

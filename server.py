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

    def generate_pokemon_names_and_images_by_colour(self, colour):
        """returns a generator containing
            (pokemon_name, pokemon_image_url)"""
        
        # list species matching colour
        pokemon_species_list = self.get_species_by_colour(colour)
        
        for pokemon_species_link in pokemon_species_list:
            print(pokemon_species_link['name'])

            # GET information about a species
            pokemon_species_json = self.get(pokemon_species_link['url'])


            # since a species may have multiple varieties
            # GET each variety
            varieties = pokemon_species_json['varieties']
            for variety in varieties:
                # (a variety is a pokemon)
                # GET the pokemon information
                pokemon_json = self.get(variety['pokemon']['url'])

                pokemon_name = pokemon_json['name']
                image_url = pokemon_json['sprites']['front_default']
                
                yield (pokemon_name, image_url)


    def get_species_by_colour(self, colour):
        colour_json = self.get(f'{COLOUR_URL}/{colour}')
        pokemon_species_list = colour_json['pokemon_species']
        return pokemon_species_list


request_cache = PokemonApiCache()

def render_pokemon_list(pokemon_generator):
    for (pokemon_name, image_url) in pokemon_generator:

        html = f'<img src="{image_url}" alt="{pokemon_name}">{pokemon_name}<br><br>'
        #html = render_template("index.html")
        yield html


# Order of routes is important

# This one will match if a colour is given
@app.route('/<colour>')
def get_by_colour(colour):

    # get (generator of) list of pokemon matching the colour
    pokemon_generator = request_cache.generate_pokemon_names_and_images_by_colour(colour)

    # take the list and render as (generator of) HTML
    return Response(render_pokemon_list(pokemon_generator))

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

# Eelda's League API and Pokemon Showdown customization

This repository contains the code used to develop a custom version of pokemon showdown with the ability to provide
validation based on external controls (which Pokémon are allowed for a specific trainer) and the ability to 
modulary customize a Pokemon Showdown server changing only specific files for easier installation without a fork of the
whole repo.

## Root folder content

The root folder of this project contains 

* `api.py`: the main program exposing REST APIs to iteract with Pokémon Showdown
            and to expose data from it for external usage
* `install/`: a folder containing the setup.py script to install the
	      new features into pokemon-showdown main folder
* `pokemon-showdown/`: a folder containing the pokemon-showdown modified
		       files to install into the main pokemon-showdown
                       project. The content of this folder follows the
		       pokemon-showdown project folder tree
* `src/`: folder containing the code used to support the main `api.py` file.
          In particular the `validator.py` files will be discussed in 
	  detail later

### api.py

The main api.py script contains flask based APIs exposing data from
the showdown ladders folder and for external team validation.

So far three endpoints are available:  

* /users/<user>
* /ladders/<ladder>
* /validate/<user>/<game_format>

#### /users/<user>

This endpoint provides the list of all users that played ranked games
on the Pokémon Showdown server and all their ranking in the formats 
providing 

# -*- coding: utf-8 -*-

import flask
from flask import request, jsonify
import pandas as pd
import glob
import ntpath
import datetime
import json
import requests

app = flask.Flask(__name__)
#app.config["DEBUG"] = True

data = '../pokemon-showdown/config/ladders/'


@app.route('/users/', defaults={'user': None})
@app.route('/users/<user>')
def user(user):
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    # Create an empty list for our results
    results = dict()
    ladders = read_data()
    ladders = ladders.groupby('Username')
    for name, group in ladders:
        if user is not None and user != name:
            continue
        results[name] = group.drop('Username', axis=1).\
            set_index('FormatID').to_dict('index')
        results[name] = [{key: results[name][key]} for key in results[name]]
    to_return = dict()
    to_return['timestamp'] = datetime.datetime.now()
    if(user is not None):
        to_return.update(results)
    else:
        to_return['Users'] = [{key: results[key]} for key in results]
    return jsonify(to_return)


@app.route('/ladders/', defaults={'ladder': None})
@app.route('/ladders/<ladder>')
def ladders(ladder):
    results = dict()
    ladders = read_data()
    ladders = ladders.groupby('FormatID')
    for name, group in ladders:
        if ladder is not None and ladder != name:
            continue
        results[name] = group.drop('FormatID', axis=1).\
            set_index('Username').to_dict('index')
        results[name] = [{key: results[name][key]} for key in results[name]]
    to_return = dict()
    to_return['timestamp'] = datetime.datetime.now()
    if(ladder is not None):
        to_return.update(results)
    else:
        to_return['Ladders'] = [{key: results[key]} for key in results]
    return jsonify(to_return)


def read_data():
    ladders = dict()
    for file in glob.glob(data+"*.tsv"):
        formato = ntpath.basename(file).split('.')[0]
        ladders[formato] = pd.read_csv(file, sep='\t')
        ladders[formato]['FormatID'] = formato
    return pd.concat(ladders)


class Pokemon:
    name = ''
    species = ''
    item = ''
    ability = ''
    moves = ['', '', '', '']
    nature = ''
    evs = [0, 0, 0, 0, 0, 0]
    gender = ''
    ivs = [31, 31, 31, 31, 31, 31]
    shiny = False
    level = 100
    happiness = 255
    types = []

    def __init__(self, mon):
        values = mon.split('|')
        self.name = values[0]
        self.species = values[1] if not values[1] == '' else values[0]
        self.item = values[2]
        self.ability = values[3]
        self.moves = values[4].split(',')
        self.nature = values[5]
        for i, value in enumerate(values[6].split(',')):
            self.evs[i] = int(value) if value != '' else 0
        self.gender = values[7]
        for i, value in enumerate(values[8].split(',')):
            self.ivs[i] = int(value) if value != '' else 31
        self.shiny = values[9] != ''
        self.level = int(values[10]) if values[10] != '' else self.level
        self.happiness = int(values[11]) if values[11] != '' else \
            self.happiness
        types = requests.get(
        'https://pokeapi.co/api/v2/pokemon/'+self.species.lower().replace(' ','-')).json()
        #print(types['types'])
        self.types=[]
        for type in types['types']:
            self.types.append(type['type']['name'])
        

    def __str__(self):
        return self.name+' @ '+self.item+'\n'+str(self.moves)+'\n' + \
            self.nature+'\n'+str(self.evs)


'''
Name|Species|Item|Ability|Moves|Nature|EVS|Gender|IVS|Shiny|Level|Happiness] x6
'''

class GymLeader:
    gym = {'capopalestra_erba':'grass',
           'capopalestra_drago':'dragon',
           'capopalestra_roccia':'rock',
           'capopalestra_buio':'dark',
           'capopalestra_volante':'flying',
           'capopalestra_acciaio':'steel',
           'capopalestra_acqua':'water',
           'capopalestra_plasma_elettro':'electric',
           'capopalestra_plasma_fuoco':'fire',
           'primo_superquattro':'efour1',
           'secondo_superquattro':'efour2',
           'terzo_superquattro':'efour3',
           'quarto_superquattro':'efour4'}
    

    def get(self,key):
        return self.gym[key]
        

def teamparser(mons):
    mons = mons.split(']')
    team = []
    for mon in mons:
        team.append(Pokemon(mon))
    return team


@app.route('/validate/<user>/<game_format>', methods=['POST'])
def validate(user=None, game_format=None):
    team = teamparser(json.loads(request.data)['team'])
    code = 200
    user_data = requests.get(
        'https://eeldasleague.it/wp-json/eelda/v1/trainer/'+user)
    user_data = user_data.json()
    print(user_data)
    print(team)
    response = ''
    to_return = {'message': 'ok'}

    if 'eelda' in game_format and (user_data['ou']==False or user_data['vgc']==False):
        code = 403
        to_return = {'message':'Utente '+user+' non partecipa alla Eelda\'s League. Iscriviti su http://eeldasleague.it'}
    
    elif user_data['gym'] and 'eelda' in game_format:
        type = GymLeader().get(user_data['gym'][0])
        for mon in team:
            #print(type)
            #print(mon.species)
            #print(mon.types)
            if type not in mon.types:
                
                response = response+mon.species +\
                    u' non è del tipo della tua palestra.\n'
                code = 403
                to_return = {'message': response}      
    elif game_format == 'gen8eeldasvgc2021series10':
        valid_mons = []
        valid_mons.extend(user_data['ou'])
        valid_mons.extend(user_data['vgc'])
        for mon in team:
            if mon.species.replace(' ','-') not in [item.replace(' ','-') for item in valid_mons]:
                response = response+mon.species +\
                    ' non presente nella tua scheda allenatore.\n'
                code = 403
                to_return = {'message': response}
    elif game_format == 'gen8eeldasou':
        for mon in team:
            if mon.species.replace(' ','-') not in [item.replace(' ','-') for item in user_data['ou']]:
                response = response+mon.species +\
                    ' non presente nel gruppo 1 della tua scheda allenatore.\n'
                code = 403
                to_return = {'message': response}
    return jsonify(to_return), code

if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='error.log',level=logging.DEBUG)
    app.run(host="0.0.0.0",port=8081)

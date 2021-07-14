# -*- coding: utf-8 -*-

import flask
from flask import request, jsonify
import pandas as pd
import glob
import ntpath
import datetime
import json
import requests
import src.validator as validator
app = flask.Flask(__name__)
#app.config["DEBUG"] = True
host = "0.0.0.0"
port = 8081
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
    print(ladders)
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




@app.route('/validate/<user>/<game_format>', methods=['POST'])
def validate(user=None, game_format=None):
    '''
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
    '''
    options = json.loads(request.data)
    options['user']=user
    return validator.handler(game_format,options)


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='error.log',level=logging.DEBUG)
    app.run(host,port=port)


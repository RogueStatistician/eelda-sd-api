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
    options = json.loads(request.data)
    options['user']=user
    return validator.handler(game_format,options)


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='error.log',level=logging.DEBUG)
    app.run(host,port=port)


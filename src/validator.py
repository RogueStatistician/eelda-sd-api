import utils as ut
import flask
from flask import request, jsonify
import pandas as pd
import glob
import ntpath
import datetime
import json
import requests


def handler(name,options):
    return dispatcher[name](options)

def get_user_data(user):
    user_data = requests.get(
        'https://eeldasleague.it/wp-json/eelda/v1/trainer/'+user)
    user_data = user_data.json()
    return user_data

def is_user_eelda(user_data):
    code = 200
    to_return = {'message':'ok'}
    if user_data['ou']==False or user_data['vgc']==False:
        code = 403
        to_return = {'message':'Utente '+user_data['username']+' non partecipa alla Eelda\'s League. Iscriviti su http://eeldasleague.it'}    
    return to_return,code

def teamparser(mons):
    mons = mons.split(']')
    team = []
    for mon in mons:
        team.append(ut.Pokemon(mon))
    return team

def vgceelda(options):
    print('cose')
    print(options)
    team = teamparser(options['team'])
    user = options['user']
    user_data = get_user_data(user)
    to_return,code = is_user_eelda(user_data)
    print(team)
    print(user_data)
    return to_return,code


dispatcher = {
    u'eeldavgc2021eelda': vgceelda
}

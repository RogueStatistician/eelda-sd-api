# -*- coding: utf-8 -*-

from . import utils as ut
import flask
from flask import request, jsonify
import pandas as pd
import glob
import ntpath
import datetime
import json
import requests


def handler(name,options):
    if dispatcher.get(name,False):
        to_return,code = dispatcher[name](options)
    else:
        code = 200
        to_return = {'message':'ok'}
    return to_return,code

def get_user_data(user):
    user_data = requests.get(
        'https://eeldasleague.it/wp-json/eelda/v1/trainer/'+user)
    user_data = user_data.json()
    if user_data['ou']:
        user_data['ou'] = [a.lower().replace(' ','').replace('-','') for a in user_data['ou']]
    if user_data['vgc']:
        user_data['vgc'] = [a.lower().replace(' ','').replace('-','') for a in user_data['vgc']]
    return user_data

def is_user_eelda(user_data):
    code = 200
    to_return = {'message':'ok'}
    if not user_data['ou'] or not user_data['vgc']:
        code = 403
        to_return = {'message':'Utente '+user_data['showdown_name']+' non partecipa alla Eelda\'s League. Iscriviti su http://eeldasleague.it'}    
    return to_return,code

def check_gym_leader(user_data,team):
    code = 200
    to_return = {'message':'ok'}
    response = ''
    gym_type = ut.GymLeader().get(user_data['gym'][0])
    for mon in team:
        if gym_type not in mon.types:
            response = response+mon.name +\
                u' non è del tipo della tua palestra.\n'
            code = 403
            to_return = {'message': response}
    return to_return,code

def teamparser(mons):
    mons = mons.split(']')
    team = []
    for mon in mons:
        team.append(ut.Pokemon(mon))
    return team

def vgceelda(options):
    team = teamparser(options['team'])
    user = options['user']
    user_data = get_user_data(user)
    to_return,code = is_user_eelda(user_data)
    response=''
    if code != 403:
        if not user_data['gym']:
            for mon in team:
                if mon.species not in user_data['ou'] and mon.species not in user_data['vgc']:
                    if user_data['pearl']=="1" and [a in user_data['ou'] or a in user_data['vgc'] for a in mon.alternatives]:
                        continue
                    response = response+mon.name +\
                    ' non presente nella tua scheda allenatore.\n'
                    code = 403
                    to_return = {'message': response}
        else:
            to_return,code = check_gym_leader(user_data,team)
    return to_return,code

def oueelda(options):
    team = teamparser(options['team'])
    user = options['user']
    user_data = get_user_data(user)
    to_return,code = is_user_eelda(user_data)
    response=''
    if code != 403:
        if not user_data['gym']:
            for mon in team:
                if mon.species not in user_data['ou']:
                    if user_data['pearl']=="1" and [a in user_data['ou'] for a in mon.alternatives]:
                        continue
                    response = response+mon.name +\
                     	' non presente nel gruppo 1 della tua scheda allenatore.\n'
                    code = 403
                    to_return = {'message': response}
        else:
            to_return,code = check_gym_leader(user_data,team)
    return to_return,code

dispatcher = {
    u'gen8eeldasvgc2021series10': vgceelda,
    u'gen8eeldasou': oueelda,

}



import flask
from flask import request, jsonify
import pandas as pd
import glob
import ntpath
import datetime
import json
import requests
import subprocess
import re

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
        self.species = values[1] if not values[1] == '' else values[0].replace(' ','').replace('-','').lower()
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
        command = "grep -n '"+self.species+":' -A 5 ../pokemon-showdown/data/pokedex.ts | grep \"types\""    
        types = subprocess.check_output(command, shell=True).decode('utf-8')
        self.types = re.search('\[(.*?)\]',types).group(1).replace('"','').lower().split(',')
        
        

    def __str__(self):
        return self.name+' @ '+self.item+'\n'+str(self.moves)+'\n' + \
            self.nature+'\n'+str(self.evs)

    def __repr__(self):
        return str(self)

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
        



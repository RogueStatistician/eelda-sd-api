import os
import sys, getopt
import shutil
import sqlite3
import hjson
from collections import OrderedDict
import re

def read_dex(showdown_root):
	dex = open(os.path.join(showdown_root,'data','pokedex.ts'),'r')
	dex = '{\n'+''.join(dex.readlines()[1:-1])+'}'
	dex_db = hjson.loads(dex)
	return dex_db


def read_weak(showdown_root):
	dex = open(os.path.join(showdown_root,'data','typechart.ts'),'r')
	dex = '{\n'+''.join(dex.readlines()[1:-1])+'}'
	dex_db = hjson.loads(dex)
	return dex_db

def read_movedex(showdown_root):
	moves = open(os.path.join(showdown_root,'data','moves.ts'),'r')
	moves = moves.readlines()[29:-1]
	pattern_start = re.compile(r'\t*[a-zA-Z]+\s*\(')
	pattern_end = re.compile(r'.*\},')
	start_ = False
	open_bracket = 0
	to_remove = list()
	for i in range(1,len(moves)):
		if not start_ :
			if pattern_start.match(moves[i]):
				start_ = True
		if start_ :
			to_remove.append(i)
			if '{' in moves[i]:
				open_bracket = open_bracket+1
			if '}' in moves[i]:
				open_bracket = open_bracket-1
			if pattern_end.match(moves[i]) and open_bracket == 0:
				start_ = False
	for i in sorted(to_remove,reverse=True):
		del moves[i]
	moves = '{\n'+''.join(moves)+'}'
	moves_db = hjson.loads(moves)
	return moves_db

def build_db(showdown_root,basedir):
	abilities_table = '''
			  CREATE TABLE IF NOT EXISTS abilities 
			  (
			   ID INTEGER PRIMARY KEY AUTOINCREMENT, 
			   ability TEXT NOT NULL
			  )
			  '''
	egg_group_table = '''
			  CREATE TABLE IF NOT EXISTS egg_groups
			  (
			   ID INTEGER PRIMARY KEY AUTOINCREMENT,
		           egg_group TEXT NOT NULL
			  )
			  '''
	types_table = '''
			 CREATE TABLE IF NOT EXISTS types
			 (
			  ID INTEGER PRIMARY KEY AUTOINCREMENT,
			  type TEXT NOT NULL
			 )
			 '''
	pokedex_table = '''
			CREATE TABLE IF NOT EXISTS pokedex
		        (
			 num INTEGER,
			 name TEXT,
			 nicename TEXT PRIMARY KEY,
			 type_1 INTEGER,
			 type_2 INTEGER,
			 HP INTEGER,
			 ATK INTEGER,
			 DEF INTEGER,
			 SPA INTEGER,
			 SPD INTEGER,
			 SPE INTEGER,
			 ability_1 INTEGER,
			 ability_2 INTEGER,
			 ability_h INTEGER,
			 heightm REAL,
			 weightkg REAL,
			 color TEXT,
			 egg_group_1 INTEGER,
			 egg_group_2 INTEGER,
			 can_gigantamax TEXT,
			 FOREIGN KEY(type_1) REFERENCES types(ID),
			 FOREIGN KEY(type_2) REFERENCES types(ID),
			 FOREIGN KEY(ability_1) REFERENCES abilities(ID),
			 FOREIGN KEY(ability_2) REFERENCES abilities(ID),
			 FOREIGN KEY(ability_h) REFERENCES abilities(ID),
			 FOREIGN KEY(egg_group_1) REFERENCES egg_groups(ID),
			 FOREIGN KEY(egg_group_2) REFERENCES egg_groups(ID)
			)
			'''
	weakness_table = '''
			CREATE TABLE IF NOT EXISTS weakness
			(
			 defending INTEGER NOT NULL,
			 attacking INTEGER NOT NULL,
			 damage REAL,
			 PRIMARY KEY(defending,attacking)
			)
			'''
	movedex_table = '''
			CREATE TABLE IF NOT EXISTS movedex
			(
				num INTEGER,
				nicename TEXT PRIMARY KEY,
				name TEXT,
				accuracy REAL,
				base_power REAL,
				category TEXT,
				pp INTEGER,
				priority INTEGER,
				type INTEGER,
				contest_type TEXT,
				FOREIGN KEY(type) REFERENCES types(ID)
			)
			'''
	db = sqlite3.connect(os.path.join(basedir,'..','db','showdown.db'))
	dex_db = read_dex(showdown_root)
	weakness_chart_db = read_weak(showdown_root)
	moves_db = read_movedex(showdown_root)
	cursor = db.cursor()
	cursor.execute('PRAGMA foreign_keys = ON')
	cursor.execute(abilities_table)
	cursor.execute(egg_group_table)
	cursor.execute(types_table)
	cursor.execute(pokedex_table)
	cursor.execute(weakness_table)
	cursor.execute(movedex_table)
	abilities = set()
	egg_groups = set()
	types = set()
	for key in dex_db:
		abilities.update(list(dex_db[key]['abilities'].values()))
		egg_groups.update(dex_db[key]['eggGroups'])
		types.update(dex_db[key]['types'])
	abilities = list(filter(None,abilities))
	egg_groups = list(filter(None,egg_groups))
	types = list(filter(None,types))
	print('\nPopulating Abilities Table')
	cursor.executemany('INSERT INTO abilities (ability) VALUES (?)',[(a,) for a in abilities])
	print('\nPopulating Egg Groups Table')
	cursor.executemany('INSERT INTO egg_groups (egg_group) VALUES (?)', [(a,) for a in egg_groups])
	print('\nPopulating Types Table')
	cursor.executemany('INSERT INTO types (type) VALUES (?)',[(a,) for a in types])
	weakness = list()
	for key in weakness_chart_db:
		defending = cursor.execute('SELECT ID FROM types WHERE lower(type)=lower(?)',(key,)).fetchone()[0]
		damage_taken = weakness_chart_db[key]['damageTaken']
		for atta in damage_taken:
			attacking = cursor.execute('SELECT ID FROM types WHERE lower(type)=lower(?)',(atta,)).fetchone()
			attacking = attacking[0] if attacking is not None else None
			damage = 1
			if damage_taken[atta] == 1:
				damage = 2
			elif damage_taken[atta] == 2:
				damage = 0.5
			elif damage_taken[atta] == 3:
				damage = 0
			if attacking is not None:
				weakness.append((defending,attacking,damage,))
	print('\nPopulating Weakness table')
	cursor.executemany('INSERT INTO weakness VALUES (?,?,?)',weakness)
	moves = list()
	for key in moves_db:
		move = moves_db[key]
		num = move['num']
		nicename = key
		name = move['name']
		accuracy = move['accuracy']
		base_power = move['basePower']
		category = move['category']
		pp = move['pp']
		priority = move['priority']
		type_ = cursor.execute('SELECT ID FROM types WHERE lower(type)=lower(?)',(move['type'],)).fetchone()
		type_ = type_[0] if type_ is not None else '???'
		contest_type = move.get('contestType',None)
		moves.append((num,nicename,name,accuracy,base_power,category,pp,priority,type_,contest_type,))
	print('\nPopulating Movedex table')
	cursor.executemany('INSERT INTO movedex VALUES (?,?,?,?,?,?,?,?,?,?)',moves)

	db.commit()
	mons = list()
	for key in dex_db:
		mon = dex_db[key]
		num = mon['num']
		name = mon['name']
		nicename = key
		type_1 = cursor.execute('SELECT ID FROM types WHERE type=?',(mon['types'][0],)).fetchone()[0]
		type_2 = None if len(dex_db[key]['types'])<2 else cursor.execute('SELECT ID FROM types WHERE type=?',(mon['types'][1],)).fetchone()[0]
		HP  = mon['baseStats']['hp']
		ATK = mon['baseStats']['atk']
		DEF = mon['baseStats']['def']
		SPA = mon['baseStats']['spa']
		SPD = mon['baseStats']['spd']
		SPE = mon['baseStats']['spe']
		ability_1 = cursor.execute('SELECT ID FROM abilities WHERE ability=?',(mon['abilities']['0'],)).fetchone()
		ability_1 = ability_1[0] if ability_1 is not None else None
		ability_2 = None if '1' not in mon['abilities'].keys() else cursor.execute('SELECT ID FROM abilities WHERE ability=?',(mon['abilities']['1'],)).fetchone()[0]
		ability_h = None if 'H' not in mon['abilities'].keys() else cursor.execute('SELECT ID FROM abilities WHERE ability=?',(mon['abilities']['H'],)).fetchone()[0]
		heightm = mon['heightm']
		weightkg = mon['weightkg']
		color = mon['color']
		egg_group_1 = cursor.execute('SELECT ID FROM egg_groups WHERE egg_group=?',(mon['eggGroups'][0],)).fetchone()[0]
		egg_group_2 = None if len(mon['eggGroups'])<2 else cursor.execute('SELECT ID FROM egg_groups WHERE egg_group=?',(mon['eggGroups'][1],)).fetchone()[0]
		can_gigantamax = mon.get('canGigantamax',None)
		mons.append((num,name,nicename,type_1,type_2,HP,ATK,DEF,SPA,SPD,SPE,ability_1,ability_2,ability_h,heightm,weightkg,color,egg_group_1,egg_group_2,can_gigantamax,))
	print('\nPopulating of Pokedex table\n')
	cursor.executemany('INSERT INTO pokedex VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',mons)
	db.commit()

def main(argv):
	usage = 'setup.py -p <path-to-pokemon-showdown>'
	basedir = os.path.dirname(__file__)
	showdown_root = ''
	try:
		opts,args = getopt.getopt(argv,"hp:",["path="])
	except getopt.GetoptError:
		print(usage)
		sys.exit(2)
	if not len(opts):
		print('required argument -p missing')
		print(usage)
		sys.exit(2)
	for opt,arg in opts:
		if opt == '-h':
			print(usage)
			sys.exit()
		elif opt in ('-p','--path'):
			showdown_root = arg
	installer_files = []
	for path,subdirs,files in os.walk(os.path.join(basedir,'..','pokemon-showdown')):
		for name in files:
			installer_files.append(os.path.join(path,name))
	print(' ______     _     _       _       _                                 ')
	print('|  ____|   | |   | |     ( )     | |                                ')
	print('| |__   ___| | __| | __ _|/ ___  | |     ___  __ _  __ _ _   _  ___ ')
	print('|  __| / _ \\ |/ _` |/ _` | / __| | |    / _ \\/ _` |/ _` | | | |/ _ \\')
	print('| |___|  __/ | (_| | (_| | \__ \ | |___|  __/ (_| | (_| | |_| |  __/')
	print('|______\___|_|\__,_|\__,_| |___/ |______\___|\__,_|\__, |\__,_|\___|')
	print('                                                    __/ |           ')
	print('                                                   |___/            ')
	print(' Pokemon Showdown Customization ')
	print('\n### Copying custom files to pokemon-showdown ###\n')
	for file in installer_files:
		path_to_file = file.split('../pokemon-showdown/')[1]
		print(path_to_file)
		os.rename(os.path.join(showdown_root,path_to_file),os.path.join(showdown_root,path_to_file)+'.old')
		shutil.copy(file,os.path.join(showdown_root,path_to_file))
	print('\n### Database creation ###\n')
	build_db(showdown_root,basedir)



if __name__ == "__main__":
	main(sys.argv[1:])



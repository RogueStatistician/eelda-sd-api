import os
import sys, getopt
import shutil
import sqlite3
import hjson
from collections import OrderedDict

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
			 nicename TEXT,
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
			 PRIMARY KEY(num,nicename),
			 FOREIGN KEY(type_1) REFERENCES types(ID),
			 FOREIGN KEY(type_2) REFERENCES types(ID),
			 FOREIGN KEY(ability_1) REFERENCES abilities(ID),
			 FOREIGN KEY(ability_2) REFERENCES abilities(ID),
			 FOREIGN KEY(ability_h) REFERENCES abilities(ID),
			 FOREIGN KEY(egg_group_1) REFERENCES egg_groups(ID),
			 FOREIGN KEY(egg_group_2) REFERENCES egg_groups(ID)
			)
			'''
	db = sqlite3.connect(os.path.join(basedir,'..','db','showdown.db'))
	dex = open(os.path.join(showdown_root,'data','pokedex.ts'),'r')
	dex = '{\n'+''.join(dex.readlines()[1:-1])+'}'
	dex_db = hjson.loads(dex)
	cursor = db.cursor()
	cursor.execute('PRAGMA foreign_keys = ON')
	cursor.execute(abilities_table)
	cursor.execute(egg_group_table)
	cursor.execute(types_table)
	cursor.execute(pokedex_table)
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
	print('\nBuilding Abilities Table\n')
	cursor.executemany('INSERT INTO abilities (ability) VALUES (?)',[(a,) for a in abilities])
	print('\nBuilding Egg Groups Table\n')
	cursor.executemany('INSERT INTO egg_groups (egg_group) VALUES (?)', [(a,) for a in egg_groups])
	print('\nBuinding Types Table\n')
	cursor.executemany('INSERT INTO types (type) VALUES (?)',[(a,) for a in types])
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
	# create_query = "create table if not exists pokedex ({0})".format(" text,".join(keys))
	# cursor.execute(create_query)
	# columns = ', '.join(keys)
	# placeholders = ':'+', :'.join(keys)
	# query = 'INSERT INTO pokedex (%s) VALUES (%s)' % (columns, placeholders)
	# for key in dex_db:
	# 	tmp = dict.fromkeys(keys)
	# 	tmp.update(dex_db[key])
	# 	print(key)
	# 	for key in tmp:
	# 		if isinstance(tmp[key],OrderedDict):
	# 			tmp[key]=str(dict(tmp[key]))
	# 		if isinstance(tmp[key],list):
	# 			tmp[key]=str(tmp[key])
	# 		#print(key+' '+str(type(tmp[key])))
	# 	cursor.execute(query, tmp)
	# db.commit()

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

	print('+--------------------------------------------+')
	print('|   Eelda\'s League Showdown Customization   |')
	print('+--------------------------------------------+')
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



import os
import sys, getopt
import shutil
import sqlite3
import hjson

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
	db = sqlite3.connect(os.path.join(basedir,'..','db','showdown.db'))
	dex = open(os.path.join(showdown_root,'data','pokedex.ts'),'r')
	dex = '{\n'+''.join(dex.readlines()[1:-1])+'}'
	dex_db = hjson.loads(dex)
	cursor = db.cursor()
	keys = set()
	for key in dex_db:
		keys.update(list(dex_db[key].keys()))
	create_query = "create table if not exists pokedex ({0})".format(" text,".join(keys))
	cursor.execute(create_query)
	columns = ', '.join(keys)
	placeholders = ':'+', :'.join(keys)
	query = 'INSERT INTO pokedex (%s) VALUES (%s)' % (columns, placeholders)
	for key in dex_db:
		tmp = dict.fromkeys(keys)
		tmp.update(dex_db[key])
		
		cursor.execute(query, tmp)
	db.commit()

if __name__ == "__main__":
	main(sys.argv[1:])



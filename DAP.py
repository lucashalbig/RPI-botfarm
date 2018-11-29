import json
from sys import executable
import argparse
import requests
from subprocess import call
from pytz import timezone
from datetime import datetime
from colorama import init, Fore, Back, Style
init()
parser = argparse.ArgumentParser(prog='getwatchABC',formatter_class=argparse.RawTextHelpFormatter, description='This python script was originally the work of @nyuszika7h and then got extensivly enhanced by @kingofusers.\n'+
Fore.RED+Style.BRIGHT+'Unlawful distribution or even usage is strictly prohibited.\nPremission is required.\n'+Style.RESET_ALL+
'DISCLAIMER: We are not responsible for any damage caused by this script.\n'+
'Keep all pets away and don\'t let them near you while you\'re working with this script.\n'+
'You have been warned! Nothing is impossible when '+Fore.YELLOW+Style.DIM+'Donald Trump'+Style.RESET_ALL+' is president.\n(Well besides a reasonable president of course and a reasonable government and etc. etc.))')
parser.add_argument('--country-code', '-cc',
                    help='CountryCode to use for fetching content...', metavar = 'DE/IT/NL/ES/FR/UK etc.', default = 'DE')
parser.add_argument('--print-urls-mode', '-pum',
                    help='Print the urls of ALL items returned for the selected show instead of selecting items to download...', action='store_true')
parser.add_argument('--no-names', '-nn',
                    help='For URL mode only: print only the urls, default: print name, then url for each item', action='store_true')
parser.add_argument('--print-video-id-list', '-pvil',
                    help='Print the video\'s kaltura-ids space seperated in one row...', action='store_true')
parser.add_argument('--show-id', '-si', 
                    help='Define a propertyID to find... (use interactive mode to find your showID)')
parser.add_argument('--only-itemsum', '-is',
                    help='Print the amount of items available and exit immediatly...', action='store_true')
parser.add_argument('--use-date', '-ud',
                    help='Use a specific date instead of shows...')
parser.add_argument('--show-name', '-sn', 
                    help='Try to find the show by it\'s name...')
parser.add_argument('--store-and-transfer', '-sat', 
                    help='Use the store and transload option of the download script...', action='store_true')
parser.add_argument('--store-no-transfer', '-snt', 
                    help='Use the store-no-transload option of the download script...', action='store_true')
parser.add_argument('--version', '-V',
                    help='Only print version of the script', action='store_true')
args = parser.parse_args()

if args.store_and_transfer:
	if args.store_no_transfer:
		print('ERROR: Can\'t use both at once!')
		exit(1)

if args.version:
	print('You are using an early alpha of this script, script is currently actually pretty useless: 0.0.1')
	exit()

if not args.print_urls_mode:
	from shutil import which
	x = which('aria2c')
	if x is None:
		print('ERROR: aria2c not found in PATH')
		exit(1)
	

#~ Use offline json file for testing purposes (no need to make unneeded requests to the disney endpoint)
useOfflineFile = True
json_offline_loc = r'defta.json'

availableCodes = 'DE/IT/NL/ES/FR/UK'.split('/')

if useOfflineFile:
	f = open(json_offline_loc, 'rb')
	
	d = f.read().decode()
	
	f.close()
	
	jso = json.loads(d)
	
	#~ print(jso)
	
	
else:
	print('Not jet implemented!')
	
shows = {'4b90600fae09350f422a8ba2':'Phineas und Ferb'}

id_vs_show_id = {}

show_obj = jso['show']
social_items = jso['social']

for item in show_obj:
	show_name = item['name']
	show_id = item['property_ids'][0]
	id = item['id']
	#~ print(f'{show_id}-{show_name}')
	shows[show_id] = show_name
	id_vs_show_id[id] = show_id
	#~ show_id_vs_id[show_id] = id

	
def isPropertyOfShow(item, showid):
	tag0 = item['tag'][0]
	if 'property_id' in tag0:
		property_id = tag0['property_id']
		if property_id not in shows:
			property_id = 'gen'
	else:
		if 'name' in tag0:
			property_id_temp = tag0['name']
			if property_id_temp in shows:
				property_id = property_id_temp
			else:
				if property_id_temp in id_vs_show_id:
					property_id = id_vs_show_id[property_id_temp]
				else:
					unassigned = {'genericStarWars':'star-wars','4ba34b58201d759e961b9666':'gen'}
					if property_id_temp in unassigned:
						property_id = unassigned[property_id_temp]
					else:
						print(property_id_temp)
						print('DEBUG INFO: ITEM:')
						print(item)
						input('Confirm to continue...')
		else:
			print('Neither propId nor name exist... DEBUG INFO: ITEM:')
			print(item)
			input('Confirm to continue...')
	if property_id == showid:
		#~ if item['object']['displayName'].startswith('Star Wars'):
			#~ print(f'{property_id!r} - {showid!r}')
			#~ print(True, item['object']['displayName'])
		return True
	else:
		return False



#~ for item in social_items:
	#~ propertyOf = None
	#~ for show in shows:
		#~ if isPropertyOfShow(item, show):
			#~ propertyOf = shows[show]
	#~ if propertyOf:
		#~ print(f'Item property of {propertyOf}')
	#~ else:
		#~ print('Item failed to obtain any property')
		#~ print(item)
		#~ input()
#~ exit()


deleteShows = []

all_items = 0
for show in shows:
	items_from_show = 0
	for item in social_items:
		if isPropertyOfShow(item, show):
			items_from_show += 1
	if items_from_show == 0:
		#~ Mark for deletion, as during iteration fails
		deleteShows.append(show)
	else:
		all_items += items_from_show
		shows[show] += f' ({items_from_show} items)'
if args.only_itemsum:
	print(f'# All itmes available: {all_items}')
	exit()

for show in deleteShows:
	del shows[show]
	


def gwpid():
	for idx, item in enumerate(shows):
		show_name = shows[item]
		print(f'{idx+1}: {show_name}')
	print()
	try:
		x = input('Select your show: ')
	except KeyboardInterrupt:
		print('\n\nInterrupted by user')
		exit(1)
	
	if x.isdigit():
		selection = int(x)
		if selection < 1 or selection > len(shows):
			print('CHECK the list above, it\'s not that hard...')
			exit(1)
		else:
			return list(shows.keys())[selection-1]
	else:
		print('Not a digit, restart the script, try again...')
		exit(1)

trailing = '?referrer=aHR0cDovL3R2LmRpc25leS5kZQ=='
http_vids = []

if not args.use_date:
	WANTED_PROPERTY_ID = gwpid()
	print()
	#~ print(WANTED_PROPERTY_ID)

	#~ exit()

	wanted_items = {}

	for item in social_items:
		name = item['object']['displayName']
		type = item['object']['objectType']
		#~ if name.startswith('Star Wars'):
			#~ print(isPropertyOfShow(item, WANTED_PROPERTY_ID))
			#~ print(WANTED_PROPERTY_ID, item, name, type)
		if isPropertyOfShow(item, WANTED_PROPERTY_ID):
			#~ continue
			if type == 'game':
				wanted_items[f'{name} - ({type})'] = item['object']['url']
			elif type == 'video':
				kaltura = item['object']['kaltura']
				kal_type = kaltura['type']
				kal_id = kaltura['id']
				type += f' / {kal_type}'
				D_URL = f'http://cdnbakmi.kaltura.com/p/1068292/sp/106829200/raw/entry_id/{kal_id}/version/0'
				wanted_items[f'{name} - ({type})'] = D_URL
			elif type == 'photo':
				image = item['object']['image']
				wanted_items[f'{name} - ({type})'] = image['url']
	#~ exit()
	print('IDX | NAME')
	for idx, name in enumerate(wanted_items):
		print(f'{idx+1:02} | {name}')
	print()
	print('Select your items (comma seperated, range permitted)...')

	def getItemList():
		try:
			x = input('Items: ')
		except KeyboardInterrupt:
			print('\n\nInterrupted by user')
			exit(1)
		items = []
		comma = x.split(',')
		for item in comma:
			if item.isdigit():
				intit = int(item)-1
				if intit in range(len(wanted_items)):
					items.append(intit)
			else:
				dash = item.split('-')
				if len(dash) == 2:
					try:
						rangestart = int(dash[0])-1
						rangeend = int(dash[1])
					except ValueError:
						start_valid = False
						if dash[0].isdigit():
							start_valid = True
						if start_valid:
							print('ERROR: Invalid range, end is invalid!')
						else:
							print('ERROR: Invalid range, start is invalid!')
						exit(1)
					if rangestart in range(len(wanted_items)):
						if rangeend in range(len(wanted_items)+1):
							for itm in range(rangestart, rangeend):
								items.append(itm)
						else:
							print('ERROR: Invalid range end, check list above')
					else:
						print('ERROR: Invalid range start, check list above')
							
		return items
	itm_list = getItemList()

	print()

	index_x = 0
	for idx, itm in enumerate(wanted_items):
		if idx in itm_list:
			index_x += 1
			URL = wanted_items[itm]
			#~ What happens with all items after selection, can likely ALWAYS be extended
			if args.print_urls_mode:
				if args.no_names:
					print(URL)
				else:
					print(itm)
					print(URL)
					print()
			else:
				r = requests.head(URL)
				if 'X-Kaltura-App' in r.headers:
					print('Nope, that\'s a fail and the reason is: {}'.format(r.headers['X-Kaltura-App']))
					#~ print('Meaning: Direct download not available, must use stream for the video.')
					#~ print('Not implemented at this point of time, will add if needed...')
					exit(5)
				else:
					http_vids.append(URL)
					print(f'Appended video to HTTP download job queue')
else:
	social_items.reverse()
	for idx, item in enumerate(social_items):
		pub = item['published']
		
		dt = datetime.strptime(f'{pub} +0000', '%Y-%m-%dT%X %z')
		berlin_dt = dt.astimezone(timezone('Europe/Berlin'))
		
		pub = berlin_dt.strftime('%Y-%m-%d, um %H:%M Uhr')
		
		pub_t = berlin_dt.strftime('um %H:%M Uhr')
		
		if pub.startswith(args.use_date):
			o = item['object']
			name = o['displayName'] + f' [{pub_t}]'
			type = o['objectType']
			if type == 'video':
				k = o['kaltura']
				kal_id = k['id']
				D_URL = f'http://cdnbakmi.kaltura.com/p/1068292/sp/106829200/raw/entry_id/{kal_id}/version/0'
				if args.print_urls_mode:
					if not args.no_names:
						print(name)
					print(D_URL)
					if not args.no_names:
						print()
				else:
					http_vids.append(D_URL)
			elif type == 'game':
				if not args.no_names:
					print(f'{name} (Spiel)')
				url = o['url']
				print(url)
				if not args.no_names:
					print()
			else:
				print(f'Obejct of type {type!r} published! Add implementation!')
				exit()

if len(http_vids)>0:
	comm = [executable,'aria2cMULTIdisney.py']
	if args.store_and_transfer:
		comm.append('-sat')
	if args.store_no_transfer:
		comm.append('-snt')
	comm.extend(http_vids)
	call(comm)

	
#~ input()
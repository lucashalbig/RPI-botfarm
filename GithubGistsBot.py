from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultCachedAudio
from telegram.ext import CommandHandler, Updater, CallbackQueryHandler, Filters
from telegram.error import TimedOut
from os.path import isfile
import logging
import requests
import time

logging.basicConfig(handlers = [logging.FileHandler('GithubGistBot.log', 'w', 'utf-8')], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
updater = Updater(token='742873885:AAE13hRxASA7Qu5lT4vK_RjXIOqGAzZcYtY')
#~ testtoken: '482467545:AAGfcWivbAWVpolN6kT_7SX30s8v3piNWCg'
dispatcher = updater.dispatcher

GISTS_API = 'https://api.github.com/gists/public'

jq = updater.job_queue

headers = {'Authorization': 'token a4339c42298a992257d0ab7eaab4a19a94854409'}

known_gists = []

def savebotdata():
	STD = open('gistBOTDATA.json', 'w')
	STD.write(json.dumps(known_gists))
	STD.close()
	return True
	
if isfile('gistBOTDATA.json'):
	print('loading bot data...', end = '', flush = True)
	STD = open('gistBOTDATA.json', 'r')
	known_gists = json.loads(STD.readline().strip())
	#~ print(user_sessions)
	print('Done')


def sendMessage(text, bot, gist_id):
    try:
        bot.send_message(chat_id='@GithubGists',  text=text, parse_mode = 'Markdown', disable_web_page_preview = True, timeout = 30)
    except TimedOut:
        print(f'sendMessage timed out on sending gist {gist_id}...')
        return sendMessage(text, bot, gist_id)


def callback_minute(bot, job):
	global known_gists
	r = requests.get(GISTS_API, headers = headers)
	gists = r.json()
	gists.reverse()
	handled_gists = 0
	for gist in gists:
		gist_id = gist['id']
		if gist_id not in known_gists:
			descr = gist['description'].replace('_',r'\_').replace('*',r'\*').replace('`',r'\`')
			if descr == '':
				descr = None
			created = gist['created_at'].replace('T',' ').replace('Z', ' (UTC)')
			files = gist['files']
			num_files = len(files)
			owner = gist['owner']
			username = owner['login']
			username_url = owner['html_url']
			gist_url = gist['html_url']
			
			text = f'*Gist created*\n{gist_url}\n'
			text += f'*Created at:* {created}\n'
			text += f'*Created by:* [{username}]({username_url})\n'
			if num_files > 1:
				text += '*Files in gist*\n'
			else:
				text += '*File in gist*\n'
			for file in files:
				filedata = files[file]
				filename = filedata['filename']
				mimetype = filedata['type']
				raw_url = filedata['raw_url']
				codelang = filedata['language']
				size = filedata['size']
				
				text += f'[{filename}]({raw_url}) (`{mimetype} - {codelang}`) - {size} Bytes\n'
			text += f'*Description:* {descr}'
			
			logging.debug('Message text: '+text)
			sendMessage(text, bot, gist_id)
			known_gists.append(gist_id)
			handled_gists += 1
	print(time.strftime(f'%D - %T: Ran once and handled {handled_gists} gists...'))
	jq.run_once(callback_minute, 60)
job_minute = jq.run_once(callback_minute, 0)


def start(bot, update):
	update.message.reply_text('This bot is only a provider for @GithubGists...\nHave a look there if you want...\n\nSend /stats for (basic) bot stats...')
	
dispatcher.add_handler(CommandHandler('start', start))


def stats(bot, update):
	update.message.reply_text(f'*Gists sent to the channel* (since bot creation): *{len(known_gists)}*', parse_mode = 'Markdown')
	
dispatcher.add_handler(CommandHandler('stats', stats))
updater.start_polling()
updater.idle()
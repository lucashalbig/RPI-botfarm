#~ Hiermit werden alle illegalen Downloads ausgeführt
import requests
#~ Hiermit werden alle Zeitreisen durchgeführt
import time
#~ Hiermit wird die gesamte Menschheit in einen Tiefschlaf versetzt
from time import sleep
#~ Hiermit wird jede Aktion geloggt, um die Nutzungsdaten nachher an die NSA zu verkaufen
import logging

from sys import exit as sexit
from os.path import isfile

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup

etag = None
disneydata = None
botdata = {}

def timeprint(text):
    print(time.strftime(f'%D - %T {text}'))

def printuser(stringy, update):
    cbq = update.callback_query
    if cbq:
        user = cbq.from_user
    else:
        user = update.message.from_user
    if user.username:
        timeprint(f'User @{user.username} has accessed {stringy}')
    else:
        firstname = user.first_name
        lastname = user.last_name
        if lastname:
            name = f'{firstname} {lastname}'
            timeprint(f'{name} has accessed {stringy}')
        else:
            timeprint(f'{firstname} has accessed {stringy}')

BOTOPTSF = 'disney.botdata'

if isfile(BOTOPTSF):
    f = open(BOTOPTSF)
    x = f.read()
    f.close()
    options = x.split('\n')
    if len(options) == 2:
        uff = options[1].format('de')
        BOT_TOKEN = options[0]
    else:
        print('FEHLER: Falsche Anzahl Optionen.')
        sexit(1)
else:
    print('FEHLER: Optionsdatei fehlt.')
    sexit(1) 

logging.basicConfig(handlers = [logging.FileHandler('DisneyNotifierBot.log', 'w', 'utf-8')], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
updater = Updater(token=BOT_TOKEN)
#~ @dnotifierbot
dispatcher = updater.dispatcher

jq = updater.job_queue

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Raspbian Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36'}

def getData():
    global disneydata
    global etag
    global shows
    if etag:
        headers.update({'If-None-Match':etag})
    r = requests.get(uff, headers = headers)
    if r.status_code == 200:
        etag = r.headers['ETag']
        disneydata = r.json()
        shows = []
        for show in disneydata['show']:
            shows.append(show['name'])
        timeprint('Neue Daten erhalten')
        return True
    elif r.status_code == 304:
        timeprint('Nix verändert auf der Seite von Disney')
        return False
    else:
        timeprint(f'Unerwarteten Status-Code erhalten {r.status_code}')
        
def stop(bot, update):
    try:
        updater.stop()
        dispatcher.stop()
        jq.stop()
        updater.idle()
    finally:
        sexit(0)
    
dispatcher.add_handler(CommandHandler('stop', stop))
    
    
def callback_minute(bot, job):
    wanted_date = time.strftime('%Y-%m-%d')
    isNew = getData()
    for possible_id in botdata:
        if possible_id.isdigit():
            object = botdata[possible_id]
            for item_wl in object['watchedlist']:
                for item in disneydata['social']:
                    published = item['published']
                    if published.startswith(wanted_date):
                        real_object = item['object']
                        if real_object['objectType'] == 'video':
                            displayName = real_object['displayName']
                            kaltura_id = real_object['kaltura']['id'].replace('_',r'\_')
                            if displayName.startswith(item_wl):
                                if kaltura_id not in botdata[possible_id]['sent_videos']:
                                    downloadURL = fr'https://cdnbakmi.kaltura.com/p/1068292/sp/106829200/raw/entry\_id/{kaltura_id}/version/0'
                                    bot.send_message(int(possible_id), f'*{displayName}*\n{downloadURL}', parse_mode = 'Markdown')
                                    botdata[possible_id]['sent_videos'].append(kaltura_id)
                        
    jq.run_once(callback_minute, 60)
job_minute = jq.run_once(callback_minute, 0)


def start(bot, update):
	update.message.reply_text('Fügen Sie eine Sendung hinzu indem sie /addSeries verwenden')
	
dispatcher.add_handler(CommandHandler('start', start))

def addSeries(bot, update, args):
    printuser('commmand /addSeries', update)
    update.message.reply_text('Bitte wählen Sie aus einer der folgenden Sendungen...')
    isNew = getData()
    keyboardrow = []
    keyboard = []
    for idx,show in enumerate(shows):
        keyboardrow.append(InlineKeyboardButton(show, callback_data = f'ADDSHOW {show}'))
        if len(keyboardrow) == 2:
            keyboard.append(keyboardrow)
            keyboardrow = []
    if len(keyboardrow) != 0:
        keyboard.append(keyboardrow)
    rm = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Bitte Sendung auswählen...', reply_markup = rm)
dispatcher.add_handler(CommandHandler('addSeries', addSeries, pass_args = True))

#~ def msghdl(bot, update):
    #~ print(update)

#~ dispatcher.add_handler(MessageHandler(Filters.text, msghdl))

def callback_query_action(bot, update):
    global botdata
    cbq  = update.callback_query
    if cbq:
        printuser(f'CBQ-Update with data {cbq.data!r}', update)
        id = str(cbq.from_user.id)
        if not id in botdata:
            botdata[id] = {'watchedlist':[],'sent_videos':[]}
        data_split = cbq.data.split(' ')
        action = data_split[0]
        del data_split[0]
        showname = ' '.join(data_split)
        if action == 'ADDSHOW':
            if showname not in botdata[id]['watchedlist']:
                botdata[id]['watchedlist'].append(showname)
                cbq.message.edit_text('Die Sendung wurde deiner Liste hinzugefügt.')
            else:
                cbq.message.edit_text('Diese Sendung hast du bereits hinzugefügt.')
        print(botdata)
        
        
dispatcher.add_handler(CallbackQueryHandler(callback_query_action))

updater.start_polling()
print('Bot startet...')
updater.idle()
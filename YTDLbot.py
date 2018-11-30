import youtube_dl
import json
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup

updater = Updater(token='718630524:AAG9K3E52ae7u1dfrWVaCUHB0AL7cvs4l8E')
dispatcher = updater.dispatcher

#~ jq = updater.job_queue

VIDEO_URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'

import logging
logging.basicConfig(handlers = [logging.FileHandler('ytdlBot.log', 'w', 'utf-8')], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def progresshandler(d):
    if d['status'] == 'finished':
        print('Download fertig.')
    else:
        print(d)

def start(bot, update):
    global printX
    global progresshandler
    def printX(message):
        update.message.reply_text(message, parse_mode = 'HTML')
    
    def progresshandler(d):
        if d['status'] == 'finished':
            printX('Download fertig.')
        else:
            printX('<b>Status: </b>'+  d['_percent_str'])
    
    printX('Bot is now assigned to you,')
    
dispatcher.add_handler(CommandHandler('start', start))

def sortingKey(thing):
    item = thing['size']
    if item.endswith('KiB'):
        realsize = float(item[:-3])*1024
    elif item.endswith('MiB'):
        realsize = float(item[:-3])*1048576
    elif item.endswith('GiB'):
        realsize = float(item[:-3])*1073741824
    return realsize
    
class MyLogger(object):
    def debug(self, msg):
        if msg.startswith('[info]'):
            video_formats = []
            info_lines = msg.split('\n')
            #~ print(json.dumps(info_lines))
            del info_lines[0]
            del info_lines[0]
            formats = []
            for line in info_lines:
                x = line.split('  ')
                plist = []
                for item in x:
                    if item.strip() != '':
                        plist.append(item)
                #~ print(plist)
                if 'audio only' in line:
                    if len(plist) == 4:
                        fmt_code, container, is_dash_audio_note, notes = plist
                        nlist = [x.strip() for x in notes.split(', ')]
                        container_info = None
                        object = {'fmtcode':fmt_code,'container': container}
                        if len(nlist) == 3:
                            #~ real_q, codec_more, size = nlist
                            #~ formats.append({'size':size, })
                            object['realq'], object['codecmore'], object['size'] = nlist
                        elif len(nlist) == 4:
                            real_q, container_info, codec_more, size = nlist
                            object['realq'], object['containerinfo'], object['codecmore'], object['size'] = nlist
                        else:
                            printX('ERROR: Additional programming required')
                        if len(nlist) in [3,4]:
                            formats.append(object)
            
                elif 'video only' in line:
                    pass
                else:
                    if len(plist) == 4:
                        fmt_code, container, res, codecinfo = plist
                        object = {'fmtcode':fmt_code,'container':container,'res':res,'codecmore': codecinfo}
                        video_formats.append(object)
            sorted_audio_formats = sorted(formats, key = sortingKey, reverse = True)
            text_message = '<b>AUDIO FORMATS</b>\n'
            for item in sorted_audio_formats:
                text_message += '<b>Format-Code (fmtcode): </b>' + item['fmtcode'] + '\n'
                text_message += '<b>Container: </b>' + item['container'] + '\n'
                text_message += '<b>Bitrate: </b>' + item['realq'] + '\n'
                text_message += '<b>Codecinfo: </b>' + item['codecmore'] + '\n'
                text_message += '<b>Size: </b>' +  item['size'] + '\n\n'
            text_message += '<b>VIDEO FORMATS</b>\n'
            for item in video_formats:
                text_message += '<b>Format-Code (fmtcode): </b>' + item['fmtcode'] + '\n'
                text_message += '<b>Container: </b>' + item['container'] + '\n'
                text_message += '<b>Resolution: </b>' + item['res'] + '\n'
                text_message += '<b>Codecinfo: </b>' + item['codecmore'] + '\n\n'
            printX(text_message)
    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        
#~ def my_hook(d):
    
        #~ print('Done downloading, now converting ...')




def getformats(bot, update):
    ydl_opts = {
        'listformats': True,
        'logger': MyLogger(),
        'progress_hooks': [progresshandler],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])
dispatcher.add_handler(CommandHandler('getformats', getformats))    

def setUrl(bot, update, args):
    global VIDEO_URL
    VIDEO_URL = args[0]
    update.message.reply_text('Video URL wurde gesetzt')
dispatcher.add_handler(CommandHandler('setUrl', setUrl, pass_args = True))    


def download(bot, update, args):
    ydl_opts = {
        'format':  args[0],
        'logger': MyLogger(),
        'progress_hooks': [progresshandler],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])
dispatcher.add_handler(CommandHandler('download', download, pass_args = True))    

updater.start_polling()
print('Bot startet...')
updater.idle()
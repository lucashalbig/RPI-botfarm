import youtube_dl
import json
import sys

def printX(message):
    print(message)


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
                        object = {'fmtcode':fmt_code,'contaliner': container}
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
                    pass
            print(sorted(formats, key = sortingKey, reverse = True))

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        
def my_hook(d):
    if d['status'] == 'finished':
        print(d)
        #~ print('Done downloading, now converting ...')


ydl_opts = {
    'listformats': True,
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
from datetime import datetime
from sys import argv, stdout
from time import sleep

countdownmode = False

if len(argv) > 1:
    event = argv[1]
    if '-cd' in argv:
        countdownmode = True
else:
    event = 'nico'
    
events = {'nico':datetime(2018,11,25,12),'mp':datetime(2018,11,23,11,45),'fp':datetime(2018,11,28,08,50)}

if event in events:
    dt = events[event]

    def calculateString(dt):
        
        dtn = datetime.now()
        dtd = dt - dtn
        days_left = dtd.days
        hours_left, calc_mins = divmod(dtd.seconds, 3600)
        hours_left += days_left * 24
        minutes_left, secs_left = divmod(calc_mins, 60)
        if minutes_left == 0:
            if hours_left == 0:
                if secs_left == 0:
                    return 'Event startet jetzt'
        if days_left < 0:
            return 'Event vorbei'
        out_s = 'Es sind noch '
        if hours_left > 0:
            out_s += f'{hours_left} Stunde(n), '
        out_s_min_left = f'{minutes_left} Minute(n), '
        if minutes_left > 0:
            out_s += out_s_min_left
        elif hours_left > 0:
            out_s += out_s_min_left
        out_s_secs_left = f'{secs_left} Sekunde(n) '
        if secs_left > 0:
            out_s += out_s_secs_left 
        elif (minutes_left > 0) or (hours_left > 0):
            out_s += out_s_secs_left 
        out_s += 'bis zum eingetragenen Zeitpunkt.'
        return out_s
    if not countdownmode:
        print(calculateString(dt))
    else:
        s = calculateString(dt)
        if s == 'Event vorbei':
            print(s)
            exit()
        while True:
            try:
                s = calculateString(dt)
                if s != 'Event vorbei':
                    stdout.write('\r'+s)
                    sleep(1)
                else:
                    print()
                    exit()
            except KeyboardInterrupt:
                print()
                exit()
else:
    print('Kein Event mit diesem Namen gefunden...')
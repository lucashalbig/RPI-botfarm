import requests
from requests.exceptions import ConnectionError
import time

errors = 0
while True:
    try:
        r = requests.get('https://ipinfo.io/json', timeout = 5)

        if r.status_code == 200:
            break
    except ConnectionError:
        errors += 1
        print(time.strftime('%T: ERROR!'))
        pass
        
x = ''
if errors > 0:
    x =  ' JETZT WIEDER'
print(time.strftime(f'%T: ES GEHT{x}! :)'))
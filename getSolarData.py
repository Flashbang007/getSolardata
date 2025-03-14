#!/usr/bin/python3.10

import os
import requests
import re
import time
import logging
from systemd.journal import JournalHandler

### vars ###
url = os.environ['SOLARURL']
pushUrl = os.environ['PUSHURL']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
monitoringUrl = os.environ['MONITORINGURL'] #comment if you dont have passive monitoring
sleeptime = 30

values = [ "webdata_now_p", "webdata_total_e", "webdata_today_e" ]

log = logging.getLogger()
log.addHandler(JournalHandler())
log.setLevel(logging.ERROR)
#log.setLevel(logging.INFO)
#log.setLevel(logging.DEBUG)

### functions ###
def make_resultobject(content: str, values: list, returnEmpty = False) -> dict:
    resultObjct = {}
    
    # returns 0 values
    if returnEmpty:
        for search in values:
            resultObjct[search] = 0
        return resultObjct

    for search in values:
        pat = re.compile(f'var {search} = "([0-9\.]+)"') # regex for js vars
        x =  re.findall(pat, content)
        
        if not x:
            raise Exception('Empty value in content')

        resultObjct[search] = x[0]

    return resultObjct

def pushData(url: str, data: dict) -> bool:
    try: 
        requests.get(url, params=data, timeout=5)
    except Exception as err:
        log.error(f"HTTP-Push-data: {err}")
        return False
    return True

### Start ###
log.info("Start Script")
resultObjct = {} # init resultobjec
resultObjctLast = {} # init last
retryFlag = False

while True:
    try: 
        requests.get(monitoringUrl) 
    except Exception as err:
        log.debug(err)

    emptynessFlag = False
    log.debug("Try HTTP request")
    try:
        response = requests.get(url, auth=(username, password), timeout=10)
    except requests.exceptions.HTTPError as err:
        log.error(err)
        continue
    except Exception as err:
        if not retryFlag: # last chance for retry
            retryFlag = True
            time.sleep(sleeptime)
            continue
        log.debug(f"HTTP-Error: {err}")
        resultObjct = make_resultobject("", values, True)
        log.debug(f"Empty result set: {resultObjct}")
        emptynessFlag = True
        retryFlag = False
    
    if not emptynessFlag:
        log.debug("Decoding html response")
        content =  response.content.decode('utf-8')
        try:
            resultObjct = make_resultobject(content, values)
            log.debug(f"Decoded resultObject: {resultObjct}")
        except Exception as err:
            log.debug(err)
            log.debug(f"Time to wait {sleeptime} sec.")
            time.sleep(sleeptime)
            continue

    # compare results and only push if different
    log.debug(f"Comparing new resultObject: {resultObjct} with last one: {resultObjctLast}")
    res = all((resultObjctLast.get(k) == v for k, v in resultObjct.items()))
    if not res:
        log.debug("Difference in result found")
        log.info(resultObjct)
        pushData(pushUrl, resultObjct)
        resultObjctLast = resultObjct
        log.debug(f"resultObjctLast is now: {resultObjctLast}")
    
    log.debug(f"Time to wait {sleeptime} sec.")
    time.sleep(sleeptime)

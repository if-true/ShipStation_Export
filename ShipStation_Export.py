import requests
import os
import random
from glob import glob
from bs4 import BeautifulSoup
import webbrowser
import datetime
import traceback
import json
import time
import pandas as pd
from datetime import timedelta


print('(make connection exceptions)')
print('add other dictionary columns to dummyframe and join')
print('remove the original column "advancdedOptions (etc)" ')
print()

try:
    os.makedirs('Output/Shipments/')
    os.makedirs('Output/Orders/')
except: pass


def send_request():
    global response
    try: response = requests.get(
        url, auth=(
            dct_passworddata['name_hashed'],
            dct_passworddata['password_hashed']),
        params={})
    except:
        print('retrying')
        time.sleep(sleeptimer)
        send_request()
        return response


##MUST USED CONVERTED KEY/PWD VALUES FROM API SITE
dct_passworddata = {
    'name_unhashed': 'YOUR_EMAIL_HERE',
    'name_hashed':'HASHED_EMAIL_HERE',
    'password_unhashed': 'YOUR_PASSWORD_HERE',
    'password_hashed':'YOUR_HASHED_PASSWORD_HERE'}


path_output = 'output/'
if not os.path.exists(path_output+'/'):
    [os.makedirs(path_output+'/'+calltype) for calltype in ['shipments','orders']]
int_subtract_this_many_days = 30000
list_frames = []
df_orders = pd.DataFrame()
input_creation_date = str(datetime.datetime.now() - timedelta(
    int_subtract_this_many_days)).split(' ')[0]
list_locations = ['Youngstown','Sacramento']



timenow = str(datetime.datetime.now()).split('.')[0]
date_range_text = input_creation_date.replace('-','.')+' - '+str(
    datetime.datetime.now()).split(' ')[0].replace('-','.')

print('Collecting Shipment Data from Shipstation...')
print('NUMBER OF DAYS INTO THE PAST: '+str(int_subtract_this_many_days))
print('Timenow: ' + timenow)
print('Date Date-Range: ' + date_range_text)
print()
print()

list_calltypes = [
    'shipments',
    'orders'
]
list_orderstatus = [
    'awaiting_payment', 'awaiting_shipment', 
    'pending_fulfillment', 'shipped', 
    'on_hold', 'cancelled']

for calltype in list_calltypes:
    ordertype = list_orderstatus[3]
    int_pages_already_collected = len(
        glob('output/'+calltype+'/*'))

    print('\nsending '+calltype)
    url = "https://ssapi.shipstation.com/"+calltype+"?showInactive=True&pageSize=500&createDateStart="+input_creation_date+"&orderStatus="+ordertype
    response = requests.get(url, auth=(
        dct_passworddata['name_hashed'],
        dct_passworddata['password_hashed']), params={})
    print('sent')

    try: dct_json_response = response.json()
    except:
        try:
            print('exception')
            soup = BeautifulSoup(response.text,'html.parser')
            dct_json_response = json.loads(soup.text)
        except:
            if response.text.lower() != 'too many request': input('broken here.')
            sleeptimer = 10
            print('initial error')
            print('sleep: '+str(sleeptimer))
            list_calltypes.append(calltype)
            time.sleep(sleeptimer)
            continue
        
    int_total_results = dct_json_response['total']
    int_page_number = dct_json_response['page']
    int_total_pages = dct_json_response['pages']
    number_of_results_on_this_page = len(dct_json_response[calltype])
    has_error = False

    print('Total Number of '+calltype.title()+': '+str(int_total_results))
    print('Pages of Results: '+str(int_total_pages))
    print('Pages Already Collected: '+str(int_pages_already_collected))

    for pagenumber in range(1,int_total_pages):
        # DONT COLLECT FINAL PAGE: MAY BE INCOMPLETE
        if has_error == True:
            print('has error')
            has_error = False
            pagenumber = pagenumber-1
        filename_output = path_output+'/'+calltype+'/_pg'+str(pagenumber)+'.csv'
        if os.path.isfile(filename_output): continue

##        sleeptimer = random.randint(1,2)
        sleeptimer = 0
##        if int(str(datetime.datetime.now()).split(' ')[1].split(
##            ':')[0]) in [21,22,23,24,0,1,2,3,4,5,6]: sleeptimer = 1
        print('sleeptimer: '+str(sleeptimer))
        time.sleep(sleeptimer)

        url = "https://ssapi.shipstation.com/"+calltype+"?showInactive=True&page="+str(pagenumber)+"&pageSize=500&sortBy=CreateDate&createDateStart="+input_creation_date+"&orderStatus="+ordertype
        response = requests.get(
            url, auth=(
                dct_passworddata['name_hashed'],
                dct_passworddata['password_hashed']),
            params={})

        print()
        print(calltype)
        print('collecting page: ' + str(pagenumber))
        ##print(url)

        try: dct_json_response = response.json()
        except:
            try:
                soup = BeautifulSoup(response.text,'html.parser')
                dct_json_response = json.loads(soup.text)            
            except:
                has_error = True
                continue
        try:
            _ = dct_json_response['Message'] == 'An error has occured'
            has_error = True
            print(dct_json_response['Message'])
            continue
        except: pass
        
        df_orders = pd.DataFrame(dct_json_response[calltype])
        int_total_results = dct_json_response['total']
        int_page_number = dct_json_response['page']
        int_total_pages = dct_json_response['pages']
        number_of_results_on_this_page = len(dct_json_response[calltype])
        
        for colname in df_orders.columns.tolist():
         try: df_orders[colname] = df_orders[colname].astype('str').str.lower()
         except: continue
        df_orders.to_csv(filename_output,index=False)


    print(calltype+' updated.')
    print('sleep: 10')
    time.sleep(10)







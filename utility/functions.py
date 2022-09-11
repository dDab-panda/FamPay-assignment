import pymongo
import os
from dotenv import load_dotenv
import requests
load_dotenv()
import json
from bson.json_util import dumps
from apscheduler.schedulers.background import BackgroundScheduler as scheduler

def get_data_from_api(api_url, parameters):
    response = requests.get(f"{api_url}", params=parameters)
    return response

def get_db():
    client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
    db = client['famPay']
    db= db['video_data']
    if len(db.index_information())<2:
        db.create_index([ ("publishedAt", -1) ])
    return db

def get_data_model(dataModel):
    result = {
        'id':dataModel['id']['videoId'],
        'publishedAt':dataModel['snippet']['publishedAt'],
        'snippet':dataModel['snippet']
        }
    return result
    
def push_data_to_db(data):
    db = get_db()
    list_yt_data = list(data['items'])
    count=0
    
    for data_item in list_yt_data:
       data_model = get_data_model(data_item)
       db_data = db.find({'id':{'$regex':data_model['id']}})
       list_db_data = list(db_data)
       if len(list_db_data)==0:
            db.insert_one(data_model)
            count+=1 
       else:
        continue

    print(count," - documents inserted in db")

cron_count=0
page_token=None
youtube_key_index=0

def get_data_from_yt_api():
    global cron_count
    global page_token
    global youtube_key_index
    cron_count+=1

    if cron_count==3:
        sch.remove_job('cron_id')

    yt_keys=os.getenv('YOUTUBE_API_KEY')
    yt_key_list = yt_keys.split(',')

    print("Cron Job Run id:",cron_count)
    params =    {
                    "key":yt_key_list[youtube_key_index],
                    "part":"id,snippet",
                    "q":"tea",
                    "publishedAfter":"2022-01-01T00:00:00Z",
                    "order":"date",
                    "type":"video",
                    "maxResults":25
                }
    if page_token is not None:
        params['pageToken'] = page_token

    response = get_data_from_api("https://www.googleapis.com/youtube/v3/search",params)    

    if response.status_code==200:
        print("sucessfully fetched the data from API")
        response_data=response.json()
        page_token = response_data['nextPageToken']     
        push_data_to_db(response_data)
    else: 
        if response.status_code==403:
            response_data=response.json()
            if response_data['error']['errors'][0]['reason'] == 'quotaExceeded':
                youtube_key_index+=1
                cron_count-=1
                print("Youtube API Quota Exhausted. API_KEY Changed")
                get_data_from_yt_api()
                
    return response_data

def start_cron_job(interval):
    if interval is None:
        interval=10

    global sch
    sch = scheduler(daemon=True)
    sch.add_job(get_data_from_yt_api,'interval', seconds=interval,id='cron_id')
    sch.start()

async def get_data_from_db_with_pg(limit, page_id):    
    db = get_db()
    if limit is None:
        limit = 9
    if page_id<1:
        page_id = 1

    skips=limit*(page_id-1)
    db_data = db.find().skip(skips).limit(limit)
    page_details = {"Page Number" : page_id,"Page Limit" : limit}
    list_db_data = list(db_data)
    list_db_data.insert(0,page_details)
    response_json = json.loads(dumps(list_db_data))

    return response_json

async def get_data_from_db():
    db = get_db()
    db_data = db.find()
    list_db_data = list(db_data)
    response_json = json.loads(dumps(list_db_data))

    return response_json

async def get_video_data_from_db_by_search(title,description):
    if title is None and description is None:
        return {"Error":"Please enter a title or description as Query Parameter"}

    if title is None:
        title=""
    if description is None:
        description="" 
           
    db = get_db()
    db_data = db.find({'$and':[{'snippet.title': {'$regex':title, '$options':'i'}},{'snippet.description': {'$regex':description, '$options':'i'}}]})
    list_db_data = list(db_data)
    data_length = {"Number of Search Results":len(list_db_data)}
    list_db_data.insert(0,data_length)
    response_json = json.loads(dumps(list_db_data))
    
    return response_json

async def get_video_data_from_db_by_search_with_pg(title,page_id):
    if title is None:
        title=""
    if page_id<1:
        page_id = 1     

    db = get_db()
    skips=9*(page_id-1)
    db_data = db.find({'snippet.title': {'$regex':title, '$options':'i'}}).skip(skips).limit(9)
    page_details = {"Page Number" : page_id,"Page Limit" : 9}
    list_db_data = list(db_data)
    list_db_data.insert(0,page_details)
    response_json = json.loads(dumps(list_db_data))
    
    return response_json


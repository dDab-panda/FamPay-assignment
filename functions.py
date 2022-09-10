import pymongo
import os
from dotenv import load_dotenv
import requests
load_dotenv()
from apscheduler.schedulers.background import BackgroundScheduler as scheduler
import json
from bson.json_util import dumps,loads

def get_data_from_api(api_url, parameters):
        response = requests.get(f"{api_url}", params=parameters)
        return response
        if response.status_code == 200:
            print("sucessfully fetched the data from API")
            return response.json()
        else:
            print(f"Hello person, there's a {response.status_code} error with your request")
            return response.json()


def getDb():
    client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
    db = client['famPay']
    db= db['video_data8']
    if len(db.index_information())<2:
        db.create_index([ ("publishedAt", -1) ])
    return db


def getDataModel(dataModel):
    result = {
        'id':dataModel['id']['videoId'],
        'publishedAt':dataModel['snippet']['publishedAt'],
        'snippet':dataModel['snippet']
        }
    return result
  

def push_data_to_db(data):

    db = getDb()
    list_yt_data = list(data['items'])
    count=0
    for dataItem in list_yt_data:
       dataModel = getDataModel(dataItem)
       db_data = db.find({'id':{'$regex':dataModel['id']}})
       list_db_data = list(db_data)
       if len(list_db_data)==0:
            db.insert_one(dataModel)
            count+=1 
       else:
        continue

    print(count," - documents inserted in db")

cron_count=0
pageToken=None
yt_key_index=0
def get_data_from_yt_api():

    global cron_count
    global pageToken
    global yt_key_index
    cron_count+=1

    if cron_count==2:
        sch.remove_job('cron_id')

    yt_keys=os.getenv('YOUTUBE_API_KEY')
    yt_key_list = yt_keys.split(',')

    print("Cron Job Run id:",cron_count)
    params =    {
                    "key":yt_key_list[yt_key_index],
                    "part":"id,snippet",
                    "q":"coding",
                    "publishedAfter":"2022-01-01T00:00:00Z",
                    "order":"date",
                    "type":"video",
                    "maxResults":25
                }
    if pageToken is not None:
        params['pageToken'] = pageToken
    response = get_data_from_api("https://www.googleapis.com/youtube/v3/search",params)    

    if response.status_code==200:
        print("sucessfully fetched the data from API")
        response_data=response.json()
        pageToken = response_data['nextPageToken']     
        push_data_to_db(response_data)
    else: 
        if response.status_code==403:
            response_data=response.json()
            if response_data['error']['errors'][0]['reason'] == 'quotaExceeded':
                yt_key_index+=1
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
    
    db = getDb()

    if limit is None:
        limit = 10
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
    
    db = getDb()

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
    db = getDb()
    db_data = db.find({'$and':[{'snippet.title': {'$regex':title, '$options':'i'}},{'snippet.description': {'$regex':description, '$options':'i'}}]})

    list_db_data = list(db_data)
    data_length = {"Number of Search Results":len(list_db_data)}
    list_db_data.insert(0,data_length)
    response_json = json.loads(dumps(list_db_data))
    
    return response_json



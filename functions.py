from pymongo import MongoClient
import os
from dotenv import load_dotenv
import requests
load_dotenv()
from apscheduler.schedulers.background import BackgroundScheduler as scheduler
import json
from bson.json_util import dumps,loads

def get_data_from_api(api_url, parameters):
        response = requests.get(f"{api_url}", params=parameters)
        if response.status_code == 200:
            print("sucessfully fetched the data from API")
            return response.json()
        else:
            print(f"Hello person, there's a {response.status_code} error with your request")


def getDb():
    client = MongoClient(os.getenv('MONGODB_URL'))
    db = client['famPay']
    db_videodata = db['video_data']
    return db_videodata

def push_data_to_db(data):

    db_videodata = getDb()
    #print(data)
    inserted = db_videodata.insert_many(data['items'])
    print(str(len(inserted.inserted_ids))," - documents inserted in db")

count=0
def get_data_from_yt_api():

    global count
    count+=1
    print("Cron Job Run id:",count)

    
    params = {
                "key":os.getenv('YOUTUBE_API_KEY'),
                "part":"id,snippet",
                "q":"Cricket",
                "publishedAfter":"022-01-01T00:00:00Z",
                "order":"date",
                "type":"video"
             }
    response_data = get_data_from_api("https://www.googleapis.com/youtube/v3/search",params)

    push_data_to_db(response_data)
    


def start_cron_job(interval):
    
    if interval is None:
        interval=10
        
    sch = scheduler(daemon=True)
    sch.add_job(get_data_from_yt_api,'interval', seconds=interval)
    sch.start()    


async def get_data_from_db_with_pg(limit, page_id):
    
    db_videodata = getDb()

    if limit is None:
        limit = 10
    if page_id<1:
        page_id = 1
    skips=limit*(page_id-1)
    
    db_data = db_videodata.find().skip(skips).limit(limit)
    page_details = {"Page Number" : page_id,"Page Limit" : limit}
    list_db_data = list(db_data)
    list_db_data.insert(0,page_details)
    response_json = json.loads(dumps(list_db_data))

    return response_json

async def get_data_from_db():
    
    db_videodata = getDb()

    db_data = db_videodata.find()
    list_db_data = list(db_data)
    response_json = json.loads(dumps(list_db_data))

    return response_json

async def get_video_data_from_db_by_search(title,description):
    
    db = getDb()
    db_data = db.find({'$and':[{'snippet.title': {'$regex':title, '$options':'i'}},{'snippet.description': {'$regex':description, '$options':'i'}}]})

    list_db_data = list(db_data)
    data_length = {"Number of Search Results":len(list_db_data)}
    list_db_data.insert(0,data_length)
    response_json = json.loads(dumps(list_db_data))
    
    return response_json
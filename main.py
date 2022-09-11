from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask,render_template
import functions
import requests

api = FastAPI()
webapp=Flask(__name__)

#Adding flask app on our FastAPI
api.mount('/app',WSGIMiddleware(webapp))

@api.get("/api/v1/start")
async def start_fetching_data_from_youtube(interval:int | None = None):
    functions.start_cron_job(interval)
    return {"message":"Cron job run successfully"}    


@api.get("/api/v1/get")
async def get_all_video_data_from_database():
    return await functions.get_data_from_db()

@api.get("/api/v1/get/page/{page_id}")
async def get_video_data_from_database_with_pagination(page_id:int,limit : int | None = None):
    return await functions.get_data_from_db_with_pg(limit,page_id)

@api.get("/api/v1/search")
async def get_video_data_from_db_by_search(title:str | None = None ,description:str | None = None):
    return await functions.get_video_data_from_db_by_search(title,description)

@api.get("/api/v1/search/page/{page_id}")
async def get_video_data_from_db_by_search_for_webapp(page_id:int,title:str | None = None):
    return await functions.get_video_data_from_db_by_search_with_pg(title,page_id)

@webapp.route('/')
def index():
    return render_template("index.html")

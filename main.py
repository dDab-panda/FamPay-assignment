from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from flask import Flask,render_template

import utility.functions as functions
api = FastAPI()

#Adding flask app on our FastAPI
webapp=Flask(__name__)
api.mount('/app',WSGIMiddleware(webapp))

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

#WebApp routing from "/" to "/app"
@api.get("/")
async def re_route_to_webapp():
    return RedirectResponse(url=f"/app/", status_code=303)

#WebApp
@webapp.route('/')
def index():
    return render_template("index.html")

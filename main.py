from fastapi import FastAPI

import functions

app = FastAPI()

@app.get("/start")
async def start_fetching_data(interval:int | None = None):
    functions.start_cron_job(interval)
    return {"message":"Cron job run successfully"}    

@app.get("/get/page/{page_id}")
async def get_video_data_from_database_with_pagination(page_id:int,limit : int | None = None):
    return await functions.get_data_from_db_with_pg(limit,page_id)

@app.get("/get")
async def get_video_data_from_database():
    return await functions.get_data_from_db()

@app.get("/search")
async def get_video_data_from_db_by_search(title:str | None = None ,description:str | None = None):
    return await functions.get_video_data_from_db_by_search(title,description)


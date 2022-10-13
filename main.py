from http.client import HTTPException
from typing import List
from fastapi import FastAPI,Request
from uuid import UUID,uuid4
#from models import User,Gender,Role, UserUpdateRequest
app = FastAPI()

items = {}

@app.on_event("startup")
async def startup_event():
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}

@app.get("/")
async def root():
    return{"Hello":"Universe"}

@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]

@app.post("/getproviderinfo")
async def getproviderinfo(info:Request):
    req_info =await info.json()
    return {
        "status":"Success",
        "data":req_info
    }
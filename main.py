from http.client import HTTPException
from tracemalloc import start
from typing import List
from unittest import result
from fastapi import FastAPI,Request
from uuid import UUID,uuid4
from load import read
from typing import Final
import json
import esteemer
#from models import User,Gender,Role, UserUpdateRequest
app = FastAPI()

items = {}
start_up_code={}
result=" "
@app.on_event("startup")
async def startup_event():
    items["foo"] = {"name": "Fighters"}
    items["bar"] = {"name": "Tenders"}
    try:
        f1=open("spek_message_id.json")
        message_code= json.load(f1)
        global start_up_code
        start_up_code["message_code"]=message_code
        #print(message_code)
        f2=open("templates.json")
        templates= json.load(f2)
        start_up_code["templates"]=templates
        #global result 
        #result= json.dumps(start_up_code)
        #print(result)
    except Exception as e:
        print("Looks like there is some problem in connection,see below traceback")
        raise e

@app.get("/")
async def root():
    return{"Hello":"Universe"}

@app.get("/items/{item_id}")
async def read_items(item_id: str):
    return items[item_id]

@app.post("/getproviderinfo")
async def getproviderinfo(info:Request):
    req_info1 =await info.json()

    #input_message = json.loads(req_info1)
    spek_tp = req_info1["@graph"]
    preferences = req_info1['Preferences']
    history=req_info1['History']
    message_code =start_up_code['message_code']
    spek_tp= json.dumps(spek_tp)
    # print(preferences)
    # print(history)
    # print(message_code)

    #spek_tp =input_message['graph']
    es = esteemer.Esteemer(spek_tp,preferences,message_code,history)
    es.transform()
    #es.apply_preferences(preferences)
    #es.apply_history(history)
    #selected_message=es.select_message()
    
    #print(selected_message)
    
    #req_info = req_info1+message_code+templates
    return {
        "status":"Success",
        "data":req_info1
    }
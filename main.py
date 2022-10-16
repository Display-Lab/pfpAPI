from http.client import HTTPException
from tracemalloc import start
from typing import List
from unittest import result
from fastapi import FastAPI,Request
from uuid import UUID,uuid4
from load import read
from typing import Final
import json
import esteemer.esteemer as esteemer
#from models import User,Gender,Role, UserUpdateRequest
app = FastAPI()

items = {}
start_up_code={}
result=" "
@app.on_event("startup")
async def startup_event():
    
    
    try:
        f1=open("./startup/spek_message_id.json")
        message_code= json.load(f1)
        global start_up_code
        start_up_code["message_code"]=message_code
        #print(message_code)
        f2=open("./startup/templates.json")
        templates= json.load(f2)
        start_up_code["templates"]=templates
        items["foo"] = {"startup": "Complete"}
        print("startup complete")
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

@app.post("/getproviderinfo/")
async def getproviderinfo(info:Request):
    req_info1 =await info.json()

    ##Running Esteemer
    spek_mc = req_info1["@graph"]
    preferences = req_info1['Preferences']
    history=req_info1['History']
    message_code =start_up_code['message_code']
    spek_mc= json.dumps(spek_mc)
    es = esteemer.Esteemer(spek_mc,preferences,message_code,history)
    es.transform()
    es.apply_preferences(preferences)
    es.apply_history(history)
    selected_message=es.select_message()
    print(selected_message)
    return {
        "status":"Success",
        "data":selected_message
    }
    

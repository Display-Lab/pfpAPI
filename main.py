from http.client import HTTPException
from typing import List
from fastapi import FastAPI,Request
from uuid import UUID,uuid4
#from models import User,Gender,Role, UserUpdateRequest
app = FastAPI()

@app.get("/")
async def root():
    return{"Hello":"Universe"}



@app.post("/getproviderinfo")
async def getproviderinfo(info:Request):
    req_info =await info.json()
    return {
        "status":"Success",
        "data":req_info
    }
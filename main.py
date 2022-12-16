from http.client import HTTPException
from tracemalloc import start
from typing import List
from unittest import result
from fastapi import FastAPI,Request
from uuid import UUID,uuid4
from load import read
from typing import Final
import json
import pandas as pd
import esteemer.esteemer as esteemer
import candidate_smasher.candidate_smasher as candidate_smasher
import mod_collector.mod_collector as mod_collector
import pictoralist
from pictoralist import Pictoralist
import thinkpudding as thinkpudding
from thinkpudding import Thinkpudding

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
        f3=open("./startup/causal_pathways.json")
        causal_pathways = json.load(f3)
        start_up_code["causal_pathways"]=causal_pathways
        items["foo"] = {"startup": "Complete"}
        print("startup complete")
    #     #global result 
    #     #result= json.dumps(start_up_code)
    #     #print(result)
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
    template=start_up_code["templates"]
    causal_pathways = start_up_code["causal_pathways"]
    
    #spek_cs_ip=''.join(map(str,req_info1["@graph"]))
    ##Running Candidate Smasher
    # print(type(req_info1))
   # print(type(req_info1["@graph"]))
    spek_bs= dict(req_info1["@graph"][0])
    print(type(spek_bs))
    content =json.dumps(spek_bs)
    md_source=json.dumps(template)
    cs = candidate_smasher.CandidateSmasher(content,md_source)
    # if cs.valid():
    spek_cs=cs.smash()
    # a=req_info1["@graph"][0]
    # l=list(a.items())[-1]
    # init = iter(l)  
    # res_dct = dict(zip(init, init))  
    # # res_dct= str(res_dct)
    # # res_dct =res_dct[1:]
    # # res_dct =res_dct[:-1]

    # l1=["@graph"]
    #print(type(a))
    file2 = open('spek_cs.json', 'w')
    file2.write(spek_cs)
    # #think pudding
    tp=Thinkpudding(spek_cs,causal_pathways)
    tp.process_causalpathways()
    tp.process_spek()
    tp.matching()
    spek_tp=tp.insert()
    # l1.append(spek_tp)
    # init1 = iter(l1)  
    # res_dct1 = dict(zip(init1, init1)) 
    
    # #spek_tp =str(res_dct1)+","+res_dct
    # # print(type(spek_tp))
    # req_info1["@graph"]=spek_tp
    # req_info1["@context"]=res_dct.get("@context")
    # file1 = open('spek_cs.json', 'w')
    # file1.writelines(spek_cs)
    # file1.close()
    ##  running think pudding-dummycode
    # spek_tp= "./tests/es_spek_tp.json"
    # with open(spek_tp, "r") as file_d:
    #     spek_tp = json.load(file_d)
    ##Running Mod Collector
    # spek_tp = req_info1
    performance_data = req_info1["Performance_data"]
    performance_data_df =pd.DataFrame (performance_data, columns = [ "Staff_Number","Measure_Name","Month","Passed_Count","Flagged_Count","Denominator","Peer_Average"])
    performance_data_df.columns = performance_data_df.iloc[0]
    performance_data_df = performance_data_df[1:]
    measure_list=[]
    measure_list=performance_data_df['Measure_Name'].drop_duplicates()
    
    # mc=mod_collector.Mod_collector(spek_tp,performance_data_df)
    # mc.transform()
    # mc.gap_calc_insert()
    # mc.trend_calc_insert()
    # mc.trend_pred()
    # spek_mc= mc.mod_collector_output()
    # ##Running Esteemer
    preferences = req_info1['Preferences']
    history=req_info1['History']
    message_code =start_up_code['message_code']
    #spek_tp= req_info1
    # dict23={}
    # dict23["@graph"]=req_info1.get("@graph")
    # dict23["@context"]=req_info1.get("@context")
    # req_info2=str(dict23)
    # req_info1=str(req_info1)
    # req_info1=eval(req_info1)
    # req_info1=str(req_info1)
    # file1 = open('spek_tp23.json', 'w')
    # file1.write(req_info1)
    
    es = esteemer.Esteemer(measure_list,spek_tp,preferences,message_code,history,performance_data_df)
    es.transform()
    #es.apply_preferences(preferences)
    # es.apply_history(history)
    selected_message = es.select_message()
    print(selected_message)

    ##Runnning Pictoralist
    # pc=pictoralist.Pictoralist(selected_message,performance_data_df)
    # pc.create_graph()
    
    return {
        "status":"Success",
        "data": selected_message
    }
    

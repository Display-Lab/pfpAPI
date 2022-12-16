import json
import sys
import warnings
import time
import logging
import json
#from asyncore import read

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper


# from .load_for_real import load
from esteemer.load_esteemer import read, transform,read_contenders,read_measures,read_comparators
from esteemer.score import score, select,apply_indv_preferences,apply_history_message

# load()

warnings.filterwarnings("ignore")
# TODO: process command line args if using graph_from_file()
# Read graph and convert to dataframe
class Esteemer():
    #start_time = time.time()
    contenders_graph = " "
    measures_graph=" "
    comparator_graph=" "
    val=" "
    val1=" "
    
    def __init__(self,measure_list, spek_tp, preferences: str = "{}", message_code: str = "{}", history: str = "{}",performance_data: pd.DataFrame=()):
        #self.spek_tp = json.dumps(spek_tp)
        #self.spek_tp = json.dumps(spek_tp)
        
        # self.spek_tp = json.dumps(spek_tp)
        # self.spek_tp = json.loads(self.spek_tp)
        self.graph_read=spek_tp
        # print(type(spek_tp))
        # file1 = open('spek_tp', 'w')
        # file1.write(spek_tp)
        
        #self.graph_read =spek_tp
        self.contenders_graph = read_contenders(self.graph_read)
        contender_messages_df = to_dataframe(self.contenders_graph)
        contender_messages_df.to_csv("spek_tp1.csv")
        
        self.measures_graph = read_measures(self.graph_read)
        self.comparator_graph = read_comparators(self.graph_read)
        self.message_code =message_code
        self.measure_list=measure_list
        self.performance_data=performance_data

    def transform(self):
        self.meaningful_messages_final = transform(self.contenders_graph,self.measures_graph,self.comparator_graph,self.measure_list)
        self.meaningful_messages_final = score(self.meaningful_messages_final)
    

    def apply_preferences(self,indv_preferences_read):
        self.applied_individual_messages,self.max_val = apply_indv_preferences(self.meaningful_messages_final,indv_preferences_read)
        global val 
        self.val = self.max_val.split('_')
        global val1
        self.val1=self.val[0]
        #print(self.val1)
    #return applied_individual_messages , val
   
    def apply_history(self,history):
        self.applied_history_filter = apply_history_message(self.applied_individual_messages,history,self.val1,self.message_code)
    
    
    def select_message (self):
    #     self.val1="line"
    #     self.applied_history_filter=self.meaningful_messages_final
    #     self.finalData = select(self.applied_history_filter,self.val1,self.message_code)
    #     #self.finalData.replace("\\", "")
    # # def verify_message(self):
    # #     self.verified_message = verify(self.finalData,self.val1,self.message_code,self.performance_data)
        message_selected_df=self.meaningful_messages_final.sample()
        message_selected_df = message_selected_df.T
        self.finalData = message_selected_df.to_json(orient="index", indent=2 )
        self.finalData.replace("\\", "")
        return self.finalData









#logging.critical("--score and select %s seconds ---" % (time.time() - start_time1))
#print(finalData)

#time_taken = time.time()-start_time
#logging.critical("---total esteemer run time according python script %s seconds ---" % (time.time() - start_time))
#print("--- %s seconds ---" % (time.time() - start_time))
"""with open('data.json', 'a') as f:
    f.write(finalData + '\n')"""

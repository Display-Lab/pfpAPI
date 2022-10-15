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
from load_esteemer import read, transform,read_contenders,read_measures,read_comparators
from score import score, select,apply_indv_preferences,apply_history_message

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
    def __init__(self, spek_tp: str = "{}", preferences: str = "{}", message: str = "{}", history: str = "{}"):
        self.graph_read=read(spek_tp)
        #print(self.graph_read)
        self.contenders_graph = read_contenders(self.graph_read)
        self.measures_graph = read_measures(self.graph_read)
        self.comparator_graph = read_comparators(self.graph_read)

    def transform(self):
        self.meaningful_messages_final = transform(self.contenders_graph,self.measures_graph,self.comparator_graph)
        self.meaningful_messages_final = score(self.meaningful_messages_final)
    

    def apply_preferences(self,indv_preferences_read):
        self.applied_individual_messages,self.max_val = apply_indv_preferences(self.meaningful_messages_final,indv_preferences_read)
        global val 
        self.val = self.max_val.split('_')
    #return applied_individual_messages , val

    def apply_history(self,history):
        self.applied_history_filter = apply_history_message(self.applied_individual_messages,history,val[0],self.message_code)
    

    def select_message (self):
    
        finalData = select(self.applied_history_filter,self.val,self.message_code)
   









#logging.critical("--score and select %s seconds ---" % (time.time() - start_time1))
#print(finalData)

#time_taken = time.time()-start_time
#logging.critical("---total esteemer run time according python script %s seconds ---" % (time.time() - start_time))
#print("--- %s seconds ---" % (time.time() - start_time))
"""with open('data.json', 'a') as f:
    f.write(finalData + '\n')"""

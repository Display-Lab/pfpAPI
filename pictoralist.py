import sys
import warnings
import time
import logging
import json
import re
import numpy as np 
import matplotlib.pyplot as plt 
#from asyncore import read

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper


from esteemer.load_esteemer import graph_from_sparql_endpoint

class Pictoralist():

    def __init__(self, selected_message: str = "{}", performance_data: pd.DataFrame=()):
        self.selected_message_dict=json.loads(selected_message)
        self.performance_data = performance_data
        self.text= self.selected_message_dict["psdo:PerformanceSummaryTextualEntity{Literal}"]
        self.measure_name= self.selected_message_dict["Measure Name"]
        self.display=self.selected_message_dict["psdo:PerformanceSummaryDisplay{Literal}"]
        self.title=self.selected_message_dict["title"]
        self.comparator=self.selected_message_dict["name"]
        self.comparison_value=self.selected_message_dict["comparison value"]
    
    def create_graph(self):
        self.graph_df = self.performance_data[self.performance_data['Measure_Name'] ==  self.measure_name]
        idx= self.graph_df.groupby(['Measure_Name'])['Month'].nlargest(4) .reset_index()
        l=idx['level_1'].tolist()
        self.last_4_measure =  self.performance_data[self.performance_data.index.isin(l)]
        try:
            self.last_4_measure['performance_data'] = (self.last_4_measure['Passed_Count'] / self.last_4_measure['Denominator'])*100
        except ZeroDivisionError:
            self.last_4_measure['performance_data'] =0
        self.comparison_value=self.comparison_value*100
        self.benchmark=[90,90,90,90]
        self.performance_data=self.last_4_measure['performance_data']
        X=self.last_4_measure['Month']
        X_axis = np.arange(len(X))
        #plt.figure(figsize=(40,30))
        plt.bar(X_axis - 0.2, self.performance_data, 0.4, label = 'Performance')
        plt.bar(X_axis + 0.2, self.benchmark, 0.4, label = 'Benchmark')
        plt.xticks(X_axis, X)
        plt.xticks(rotation =45)
        plt.xlabel("Month")
        plt.ylabel("Performance")
        plt.title("Performance")
        plt.legend()
        plt.show()


        #self.last_4_measure.to_csv("last4measure.csv")
        

        

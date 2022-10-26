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
            self.last_4_measure['performance_data'] =(self.last_4_measure['Passed_Count'] / self.last_4_measure['Denominator'])*100
        except ZeroDivisionError:
            self.last_4_measure['performance_data'] =0.0
        #self.last_4_measure['performance_data'] =  self.last_4_measure['performance_data'].round(decimals = 1)
        self.comparison_value=self.comparison_value*100
        self.peer_average= self.last_4_measure["Peer_Average"]
        self.benchmark=[90,90,90,90]
        self.performance_data=self.last_4_measure['performance_data']
        

        self.last_4_measure['Date'] = pd.to_datetime(self.last_4_measure['Month'])
        self.last_4_measure['year']= pd.DatetimeIndex(self.last_4_measure['Month']).year
        self.last_4_measure['month1'] = pd.DatetimeIndex(self.last_4_measure['Month']).month
        self.last_4_measure['year']=self.last_4_measure['year'].astype(str)
        self.last_4_measure['month1']=self.last_4_measure['month1'].astype(str)+"/"
        X=self.last_4_measure['month1']+self.last_4_measure['year']
        X_axis = np.arange(len(X))
        #plt.figure(figsize=(40,30))
        X_p=X_axis - 0.2
        X_b=X_axis + 0.2
        X_g = X_axis-0.4
        self.performance_data = self.performance_data.tolist()
        self.performance_data = [round(item, 2) for item in self.performance_data]
        self.peer_average = self.peer_average.tolist()
        plt.plot(X_g,self.benchmark)
        line=plt.bar(X_p, self.performance_data, 0.4, label = 'Performance')
        line1=plt.bar(X_b, self.peer_average, 0.4, label = 'Peer Average')
        for i in range(len(self.performance_data)):
            plt.annotate(str(self.performance_data[i]), xy=(X_p[i],self.performance_data[i]), ha='center', va='bottom',xytext=(X_p[i],self.performance_data[i]-10))
        for i in range(len(self.peer_average)):
            plt.annotate(str(self.peer_average[i]), xy=(X_b[i],self.peer_average[i]), ha='center', va='bottom',xytext=(X_b[i],self.peer_average[i]-10))
        plt.xticks(X_axis,X)
        
        #X=X.tolist()
        plt.xlim(left=-0.4)
        #plt.xlim(X[0],X[len(X)-1])
        #plt.xticks(rotation =45)
        plt.xlabel("Month")
        plt.ylabel("Performance")
        plt.title("Your Performance for the measure "+self.measure_name)
        plt.legend(bbox_to_anchor=(1, 0), loc="lower right")
        #plt.legend(bbox_to_anchor=(-0.75, -0.15), loc="lower left")
        #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox = True, shadow = True)
        plt.show()


        #self.last_4_measure.to_csv("last4measure.csv")
        

        

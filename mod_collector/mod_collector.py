#from asyncore import read
import json
import sys
import warnings
import time
import logging
import json
import re
#from asyncore import read

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper



from mod_collector.load_mod_collector import  read, transform,read_contenders,read_measures,read_comparators,read_for_insert
from mod_collector.calc_gaps_slopes import gap_calc,trend_calc,monotonic_pred
from mod_collector.insert import insert_gap,insert_trend ,insert_slope

class Mod_collector():
    contenders_graph = " "
    measures_graph=" "
    comparator_graph=" "
    def __init__(self, spek_tp: str = "{}", performance_data: pd.DataFrame=()):
       
        self.spek_tp = json.dumps(spek_tp)
        self.graph_read=read(self.spek_tp)
        self.performance_data = performance_data
        self.contenders_graph = read_contenders(self.graph_read)
        self.measures_graph = read_measures(self.graph_read)
        self.comparator_graph = read_comparators(self.graph_read)
        #self.spek_tp_insert =json.dumps(spek_tp_insert)
        #self.spek_tp_input1=read_for_insert(self.spek_tp_insert)
       
    
    def transform(self):
        self.comparison_values = transform(self.contenders_graph,self.measures_graph,self.comparator_graph)

    def gap_calc_insert(self):
        self.gap_size= gap_calc( self.performance_data, self.comparison_values)
        self.gap_graph =insert_gap(self.gap_size,self.graph_read)

    def trend_calc_insert(self):
        self.trend_slope=trend_calc(self.performance_data,self.comparison_values)
        self.slope_graph =insert_slope(self.trend_slope,self.gap_graph)
    def trend_pred(self):
        self.monotonic_pred_df = monotonic_pred(self.performance_data,self.comparison_values)
        self.trend_graph = insert_trend(self.monotonic_pred_df,self.slope_graph)
    def mod_collector_output(self):
        #return self.trend_graph.serialize(format='json-ld', indent=4)
        return self.trend_graph

    
# graph_read = read(sys.argv[1])
# performance_data_df = pd.read_csv(sys.argv[2])

# #indv_preferences_read_df = pd.read_json(sys.argv[2], lines=True)
# contenders_graph = read_contenders(graph_read)
# measures_graph = read_measures(graph_read)
# comparator_graph = read_comparators(graph_read)
# print(contenders_graph)
# contenders_graph=graph_from_sparql_endpoint("http://localhost:3030/ds/sparql")
# print(contenders_graph.serialize(format="ttl"))
# Transform dataframe to more meaningful dataframe





# monotonic_pred_df = monotonic_pred(performance_data_df,comparison_values)
# trend_graph = insert_trend(monotonic_pred_df,gap_graph)
# print(trend_graph.serialize(format='json-ld', indent=4))


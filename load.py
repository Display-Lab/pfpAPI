import warnings
import time
import logging

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper

warnings.filterwarnings("ignore")
def read(file):
    start_time = time.time()
    g = Graph()
    g.parse(file)
    
    
    logging.critical(" reading graph--- %s seconds ---" % (time.time() - start_time)) 
    return g
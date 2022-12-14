from rdflib import Graph, ConjunctiveGraph
    
@app.on_event("startup")
async def startup_event():

    # create a conjunctive graph with one part being the base graph

    g = ConjunctiveGraph

    baseGraph = Graph()

    # load templates into base graph
    # load cps into base graph
    # add base graph to global graph "g"
    
    # Maybe extract goal comparators from measures

@app.post("/createprecisionfeedback/")
async def createprecisionfeedback(req:Request):

    performerGraph: Graph = createPerformerGraph(req)

    # add performerGraph to "g"

    performanceData: DataFrame = extractPerformanceData(req)
    preferenceData: DataFrame = extractPreferenceData(req)
    historyData: DataFrame = extractHistoryData(req) # Isn't this really a collection of "messages"?
        
    # maybe extract benchmarks to a suitable data structure (e.g. Dataframe)

    bitStomach(g,performanceData) # update performer graph with performance content generated by annotations (plus add moderators to performance content)

    candidateSmasher(g) # update performer graph with candidates genarated from templates and perfomance content in the performer graph

    # ^^ maybe candidate smasher should create a separate candidate graph (added to "g") for efficiency

    thinkPudding(g) # adds "acceptableBy" to some candidates based on the causal pathwys

    esteemer(g, preferenceData, historyData) # # adds "selected" to one candidates based on additional ranking/valuation

    message = generateMessage(g, performanceData) # retuns a json message to be passed back throught the api; includes history, measure, performance content, image function from message template, etc.

    pictoralist(message) # add base64 encoded image (if needed) genarated using image function specified in message and history, performance content, benchmarks, etc. in the message

    return message


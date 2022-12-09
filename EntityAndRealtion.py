import nltk, re
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")

from transformers import pipeline

ner = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")


# tokenized question
def tokenize(question):
    tokens = nltk.word_tokenize(question)
    pos_tokens = nltk.pos_tag(tokens)
    return pos_tokens


def getEnt(question):
    entities = ner(question, aggregation_strategy="simple")
    entList = []
    for ent in entities:
        entList.append(ent["word"])
    return entList


# Case-insensitive search for entity
def getEntURI(graph, entity):
    # entity label to URIs
    print('''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>

        SELECT ?sujU
        WHERE{{
            ?sujU rdfs:label "{}"@en.
            }}'''.format(entity))

    query_entURI_slow = '''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>
        SELECT ?sujU
        WHERE{{
            ?sujU rdfs:label ?label.
            FILTER(regex(?label, "{}"@en, "i"))
            }}
            LIMIT 3'''.format(entity)
    query_entURI = '''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>
        SELECT ?sujU        
        WHERE{{
            ?sujU rdfs:label "{}"@en.
            }}'''.format(entity)
    entURIList = list(graph.query(query_entURI))
    entURIs = []
    for entURI in entURIList:
        entURIs.append(str(entURI[0]))
    print("entURI: ", entURIs)
    if len(entURIs) == 0:
        entURIList = list(graph.query(query_entURI_slow))
        entURIs = []
        for entURI in entURIList:
            entURIs.append(str(entURI[0]))
        print("entURI with slow: ", entURIs)
    return entURIs


# helper function to get the ID of the entity
def getEntIdByURI(WD, entURI):
    entId = []
    if WD in entURI:
        wdIdPattern = "{}(.*)".format(WD)
        entId = re.search(wdIdPattern, entURI).group(1)
    return entId


def returnVerbs(pos_tokens):
    idxlist = []
    verbTokens = []
    for idx, tup in enumerate(pos_tokens):
        if "VB" in tup[1]:
            idxlist.append(idx)
    for idx in idxlist:
        verbTokens.append(pos_tokens[idx][0])
    return verbTokens

    # this method match the ... of pattern


def theOfTokens(question):
    matching = re.search("the (.*) of", question)
    if not matching:
        return False
    else:
        relation = matching.group(1)
        return [relation]


# Get relation relation
def getRel(question):
    theOf = theOfTokens(question)
    if not theOf:
        pos_tokens = tokenize(question)
        verbs = returnVerbs(pos_tokens)
        relations = verbs
    else:
        relations = theOf
    # Hard coded relation, since it won't detect it otherwise
    if "recommend" in question.lower():
        relations = ['recommend']
    if "directed" in question.lower():
        relations = ['director']
    if "director" in question.lower():
        relations = ['director']
    return relations


# get relation pid by relation labels
def getRelWDTid(graph, WDT, relations):
    relURIList = getRelURI(graph, relations, WDT)
    relIds = []
    for row in relURIList:
        print("row: ", row)
        if WDT in row:
            wdtIdPattern = "{}(.*)".format(WDT)
            relId = re.search(wdtIdPattern, row).group(1)
            relIds.append(relId)
    return relIds


def getRelURI(graph, relation, WDT):
    # get Rel URI
    query_relURI = '''
           prefix wdt: <http://www.wikidata.org/prop/direct/>
           prefix wd: <http://www.wikidata.org/entity/>

           SELECT ?rel WHERE{{
               ?rel rdfs:label "{}"@en.
               }}'''.format(relation)
    relURIList = list(graph.query(query_relURI))
    relURIs = []
    for relURI in relURIList:
        print(relURI)
        if WDT in str(relURI[0]):
            relURIs.append(str(relURI[0]))
    return relURIs

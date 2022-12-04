import nltk, re
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")

from transformers import pipeline

ner = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")


# parse the message and get entity
def parseEnt(self, graph):
    # classify the message
    entitylist = getEnt(self.message)
    entList = []
    print("Entity list:", entitylist)
    for entity in entitylist:
        # check if URI exist
        self.entURI = getEntURI(graph, entity)
        # if exist, then append entity label
        if len(self.entURI) != 0:
            print('entURI exist')
            entList.append(entity)
        # if not, then query typo
        else:
            print('entURI does not exist')
    print(entList)
    return entList


# parse the relation
def parseRel(self, entity, graph, WDT):
    relationList = getRel(self.message)
    print("parseRel", entity, relationList)
    if 'recommend' not in relationList:
        relationListToReturn = []
        for relation in relationList:
            print("relation:", relation)
            relURI = getRelURI(graph, relation, WDT)
            if len(relURI) != 0:
                relationListToReturn.append(relation)
            # if not, then query alias
            else:
                print('relURI does not exist')

    else:
        relationListToReturn = ['recommend']
    return relationListToReturn
# tokenized question
def tokenize(question):
    tokens = nltk.word_tokenize(question)
    pos_tokens = nltk.pos_tag(tokens)
    return pos_tokens


def returnNouns(pos_tokens):
    idxlist = []
    nouns = []
    for idx, tup in enumerate(pos_tokens):
        if "NN" in tup[1]:
            idxlist.append(idx)
    for idx in idxlist:
        nouns.append(pos_tokens[idx][0])
    return nouns


def returnNounBfMovie(pos_tokens):
    movieIdx = 0
    for idx, tup in enumerate(pos_tokens):
        if "movie" in tup[0].lower() or "film" in tup[0].lower():
            movieIdx = idx
    for idx, tup in enumerate(pos_tokens):
        if idx == movieIdx - 1 and "NN" in tup[1]:
            genre = pos_tokens[idx][0]
            return genre


def getEnt(question):
    entities = ner(question, aggregation_strategy="simple")
    entList = []
    for idx, ent in enumerate(entities):
        entList.append(ent["word"])
    return entList


def getEntURI(graph, entity):
    # entity label to URIs

    print('''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>

        SELECT ?sujU
        WHERE{{
            ?sujU rdfs:label "{}"@en.
            }}'''.format(entity))

    query_entURI = '''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>

        SELECT ?sujU
        WHERE{{
            ?sujU rdfs:label "{}"@en.
            }}'''.format(entity)
    entURIList = list(graph.query(query_entURI))
    entURIs = []
    for idx, entURI in enumerate(entURIList):
        entURIs.append(str(entURI[0]))
    print("entURI: ", entURIs)
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
    # Hard coded relation, since it wont detect it otherwise
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
    for idx, row in enumerate(relURIList):
        print("idx: ", idx, "row: ", row)
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
    for idx, relURI in enumerate(relURIList):
        print(relURI)
        if WDT in str(relURI[0]):
            relURIs.append(str(relURI[0]))
    return relURIs


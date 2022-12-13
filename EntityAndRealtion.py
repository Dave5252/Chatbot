import nltk, re
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")

from transformers import pipeline

ner = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")


def tokenize(question):
    """
    Tokenize the question
    :param question: raw question from the user
    :return: tokenized question in a list
    """
    tokens = nltk.word_tokenize(question)
    pos_tokens = nltk.pos_tag(tokens)
    return pos_tokens


def getEnt(question):
    """
    Get the entity from the question
    :param question: tokenized question
    :return: Entity list
    """
    entities = ner(question, aggregation_strategy="simple")
    entList = []
    for ent in entities:
        entList.append(ent["word"])
    return entList


def getEntURI(graph, entity):
    """
    Get the entity URI from the entity label
    :param graph: graph
    :param entity: An entity label
    :return: the entity URI
    """
    # entity label to URIs
    print('''
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>

        SELECT ?sujU
        WHERE{{
            ?sujU rdfs:label "{}"@en.
            }}'''.format(entity))
    # entity label to URIs with the filter
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
    """
    Get the entity ID from the entity URI
    :param WD: the Wikidata prefix
    :param entURI: the entity URI
    :return: the entity ID
    """
    entId = []
    if WD in entURI:
        wdIdPattern = "{}(.*)".format(WD)
        entId = re.search(wdIdPattern, entURI).group(1)
    return entId


def returnVerbs(pos_tokens):
    """
    Get the verbs from the tokenized question
    :param pos_tokens: Tokenized question
    :return: return the verbs
    """
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
    """
    Get the tokens between "the (.*) of" in the question
    :param question: the question
    :return: the tokens between "the (.*) of"
    """
    matching = re.search("the (.*) of", question)
    if not matching:
        return False
    else:
        relation = matching.group(1)
        return [relation]


def getRel(question):
    """
    Get the relation from the question
    :param question: the question
    :return: The relation
    """
    # check if the question has the "the (.*) of" pattern
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


def getRelWDTid(graph, WDT, relations):
    """
    Get the relation ID from the relation URI
    :param graph: the graph
    :param WDT: the Wikidata prefix
    :param relations: the relation
    :return: the relation IDs
    """
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
    """
    Get the relation URI from the relation label
    :param graph:  the graph
    :param relation: the relation label
    :param WDT: the Wikidata prefix
    :return: the relation URI
    """
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

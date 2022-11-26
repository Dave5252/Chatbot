import nltk, re, editdistance
from sklearn.metrics import pairwise_distances
# from https://huggingface.co/Jean-Baptiste/camembert-ner
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")

# Process text sample (from wikipedia)

from transformers import pipeline

ner = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# tokenized question
def getTokens(question):
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


def returnNAfRcmd(pos_tokens):
    idxlist = []
    words = []
    recIdx = 999
    for idx, tup in enumerate(pos_tokens):
        if "recommend" in tup[0].lower():
            recIdx = idx
        if idx > recIdx and "NN" in tup[1]:
            idxlist.append(idx)
    for idx in idxlist:
        words.append(pos_tokens[idx][0])
    return words


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

    print( '''
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


def getEntIdByURI(WD, entURI):
    entId = []
    if WD in entURI:
        wdIdPattern = "{}(.*)".format(WD)
        entId = re.search(wdIdPattern, entURI).group(1)
    return entId


def checkTypo(entLblList, entity):
    entTypoCorr = []
    threshold = 9999
    for idx, entlbl in enumerate(entLblList):
        dist = editdistance.eval(entity, entlbl)
        if dist < threshold:
            threshold = dist
            matchnode = idx
    entTypoCorr = entLblList[matchnode]
    return entTypoCorr


# TODO delete this method
def getNearestEntEmb(WD, ent2id, ent2lbl, lbl2ent, id2ent, entity_emb, word):
    ent = ent2id[lbl2ent[word]]
    emb = entity_emb[ent]
    dist = pairwise_distances(emb.reshape(1, -1), entity_emb).reshape(-1)
    most_likely = dist.argsort()
    qids = []
    lbls = []
    for rank, idx in enumerate(most_likely[:15]):
        qids.append(id2ent[idx][len(WD):])
        lbls.append(ent2lbl[id2ent[idx]])
    return qids, lbls


# TODO delete this method
def clarifyEnt(qids, lbls):
    qid = qids[10]
    lbl = lbls[10]
    return qid, lbl


def getTokens(question):
    tokens = nltk.word_tokenize(question)
    pos_tokens = nltk.pos_tag(tokens)
    return pos_tokens


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
    theOfPattern = "the (.*) of"
    matching = re.search(theOfPattern, question)
    if not matching:
        print("no match for the of pattern")
        return False
    else:
        relation = matching.group(1)
        return [relation]

# Get relation relation
def getRel(question):
    theOf = theOfTokens(question)
    if not theOf:
        pos_tokens = getTokens(question)
        verbs = returnVerbs(pos_tokens)
        relations = verbs
    else:
        relations = theOf
     # Hard coded relation, since it vant detect it
    if "recommend" in question.lower():
        relations = ['recommend']
    if "directed" in question.lower():
        relations = ['director']
    if "director" in question.lower():
        relations = ['director']
    return relations

# search for alias of relation in predAlias dictionary
def searchAlias(relation, predAlias):
    swdtPropList = []
    for idx, alt in enumerate(predAlias['propertyAltLabel']):
        # print(idx,alt)
        if isinstance(alt, str):
            listAlt = list(alt.split(', '))
        # print(listAlt)
        if relation in listAlt:
            pd = predAlias.iloc[[idx]]
            wdtProp = pd['propertyLabel']
            swdtProp = wdtProp[pd.index.values[0]]
            swdtPropList.append(swdtProp)
        elif predAlias.iloc[idx].str.contains(relation)['propertyAltLabel'] and isinstance(
                predAlias.iloc[idx]['propertyAltLabel'], str):
            pd = predAlias.iloc[[idx]]
            wdtProp = pd['propertyLabel']
            swdtProp = wdtProp[pd.index.values[0]]
            swdtPropList.append(swdtProp)

    return swdtPropList

    # get relation pid by relation labels


def getRelWDTid(graph, WDT, relations):
    relURIList = getRelURI(graph, relations, WDT)
    relIds = getRelIdByURI(WDT, relURIList)
    return relIds

    # query for relation URI with relation label as input


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


def getRelIdByURI(WDT, relURIList):
    # get Rel WDTid
    relIds = []
    for idx, row in enumerate(relURIList):
        print("idx: ", idx, "row: ", row)
        if WDT in row:
            wdtIdPattern = "{}(.*)".format(WDT)
            relId = re.search(wdtIdPattern, row).group(1)
            relIds.append(relId)
    return relIds

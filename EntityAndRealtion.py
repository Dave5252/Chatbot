import nltk, re, editdistance
from transformers import pipeline
from sklearn.metrics import pairwise_distances

ner = pipeline('ner')


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

    ## this method match the ... of pattern


def theOfTokens(question):
    theOfPattern = "the (.*) of"
    matching = re.search(theOfPattern, question)
    if not matching:
        return False
    else:
        relation = matching.group(1)
        return [relation]
    ## main method for getting relation


def getRel(question):
    theOf = theOfTokens(question)
    if not theOf:
        tbd = True
        pos_tokens = getTokens(question)
        verbs = returnVerbs(pos_tokens)
        relations = verbs
    else:
        tbd = False
        relations = theOf
    return relations, tbd

    ## check if recommend in relation


def tbdRel(relation):
    if 'recommend' in relation:
        return ['recommend']
    return relation

    ## search for alias of relation in predAlias dictionary


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

    ## get relation pid by relation labels


def getRelWDTid(graph, WDT, relations):
    relURIList = getRelURI(graph, relations, WDT)
    relIds = getRelIdByURI(WDT, relURIList)
    return relIds

    ## query for relation URI with relation label as input


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
    print("relURI: ", relURIs)
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




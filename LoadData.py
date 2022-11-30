import logging

import numpy as np
import pandas as pd
import json, csv, rdflib
from rdflib.term import URIRef, Literal

# %%
# define some prefixes
WD = rdflib.Namespace('http://www.wikidata.org/entity/')
WDT = rdflib.Namespace('http://www.wikidata.org/prop/direct/')
DDIS = rdflib.Namespace('http://ddis.ch/atai/')
RDFS = rdflib.namespace.RDFS
SCHEMA = rdflib.Namespace('http://schema.org/')

# %%
# load the graph
graph = rdflib.Graph().parse(r'C:\Users\David\Desktop\Chatbot\Data\14_graph.nt', format='turtle')
# load the embeddings
entity_emb = np.load(r'C:\Users\David\Desktop\Chatbot\Data\entity_embeds.npy')
relation_emb = np.load(r'C:\Users\David\Desktop\Chatbot\Data\relation_embeds.npy')
logging.info('Loading embeddings')
# load the images
# load the dictionaries
with open(r'C:\Users\David\Desktop\Chatbot\Data\entity_ids.del', 'r') as ifile:
    ent2id = {rdflib.term.URIRef(ent): int(idx) for idx, ent in csv.reader(ifile, delimiter='\t')}
    id2ent = {v: k for k, v in ent2id.items()}
with open(r'C:\Users\David\Desktop\Chatbot\Data\relation_ids.del', 'r') as ifile:
    rel2id = {rdflib.term.URIRef(rel): int(idx) for idx, rel in csv.reader(ifile, delimiter='\t')}
    id2rel = {v: k for k, v in rel2id.items()}
# load the embeddings
ent2lbl = {ent: str(lb) for ent, lb in graph.subject_objects(RDFS.label)}
lbl2ent = {lb: ent for ent, lb in ent2lbl.items()}
entities = set(graph.subjects()) | {s for s in graph.objects() if isinstance(s, URIRef)}
# all subjects and the objects which isinstance of URIRef are entities
predicates = set(graph.predicates())
literals = {s for s in graph.objects() if isinstance(s, Literal)}

# %%
# load imdb data
top250 = set(open(r'C:\Users\David\Desktop\Chatbot\Data\imdb-top-250.t').read().split('\n')) - {''}

print(pd.DataFrame([
    ('Top-250 coverage', '{:n}'.format(
        len(top250 & {str(o) for o in graph.objects(None, WDT.P345) if o.startswith('tt')}))),
    ('Entities with IMDb ID', '{:n}'.format(  # IMDB ID
        len({str(o) for o in graph.objects(None, WDT.P345) if o.startswith('tt')}))),
    ('Plots linked to a movie', '{:n}'.format(
        len({qid for qid, plot in csv.reader(open(r'C:\Users\David\Desktop\Chatbot\Data\plots.csv', encoding='utf-8'))
             if
             URIRef(qid) in entities}))),
    ('Comments linked to a movie', '{:n}'.format(
        len([qid for qid, rating, sentiment, comment in
             csv.reader(open(r'C:\Users\David\Desktop\Chatbot\Data\user-comments.csv')) if
             URIRef(qid) in entities]))),
    ('Movies having at least one comment', '{:n}'.format(
        len({qid for qid, rating, sentiment, comment in
             csv.reader(open(r'C:\Users\David\Desktop\Chatbot\Data\user-comments.csv')) if
             URIRef(qid) in entities}))),
]))
# %%
# from dataset_intro notebook
ent_lit_preds = {p for s, p, o in graph.triples((None, None, None)) if isinstance(o, Literal)}
print(pd.DataFrame([
    ('# entities', '{:n}'.format(
        len(entities))),
    ('DDIS.rating', '{:n}'.format(
        len(set(graph.subjects(DDIS.rating, None))))),
    ('DDIS.tag', '{:n}'.format(
        len(set(graph.subjects(DDIS.tag, None))))),
    ('SCHEMA.description', '{:n}'.format(
        len({s for s in graph.subjects(SCHEMA.description, None) if s.startswith(WD)}))),
    ('RDFS.label', '{:n}'.format(
        len({s for s in graph.subjects(RDFS.label, None) if s.startswith(WD)}))),
    ('WDT.P18 (wikicommons image)', '{:n}'.format(
        len(set(graph.subjects(WDT.P18, None))))),
    ('WDT.P2142 (box office)', '{:n}'.format(
        len(set(graph.subjects(WDT.P2142, None))))),
    ('WDT.P345 (IMDb ID)', '{:n}'.format(
        len(set(graph.subjects(WDT.P345, None))))),
    ('WDT.P577 (publication date)', '{:n}'.format(
        len(set(graph.subjects(WDT.P577, None))))),
]))
# %%
# load images
with open(r'C:\Users\David\Desktop\Chatbot\Data\images.json', "r") as f:
    images = json.load(f)

# TODO: delete this
# %%
# entity labels into list, for later use
#entLabelList = [str(o) for o in graph.objects(None, RDFS.label)]
#predURIList = list(predicates)
#predWDTlist = []
#predLblList = []
#for idx, prd in enumerate(predURIList):
#
#    wdtIdPattern = "{}(.*)".format(WDT)
#    if re.search(wdtIdPattern, prd):
#        predWDT = re.search(wdtIdPattern, prd).group(1)
#    predWDTlist.append(predWDT)
#
#def getRelLbl(graph, rel):
#    # get Rel URI
#    query_relLbl = '''
#            prefix wdt: <http://www.wikidata.org/prop/direct/>
#            prefix wd: <http://www.wikidata.org/entity/>
#
#            SELECT ?relLbl WHERE{{
#                wdt:{} rdfs:label ?relLbl.
#                }}'''.format(rel)
#    relLbl = graph.query(query_relLbl)
#    return relLbl
#
#
#for idx, pred in enumerate(predWDTlist):
#    predLbl = str(list(getRelLbl(graph, pred))[0][0])
#    predLblList.append(predLbl)
#    print(predLblList[idx])
#
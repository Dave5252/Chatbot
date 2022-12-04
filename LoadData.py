import logging

import numpy as np
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
# load images
with open(r'C:\Users\David\Desktop\Chatbot\Data\images.json', "r") as f:
    images = json.load(f)

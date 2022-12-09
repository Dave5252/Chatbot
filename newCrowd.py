import pandas as pd

from EntityAndRealtion import getRelWDTid, getEntURI, getEntIdByURI

import logging

import numpy as np
import json, csv, rdflib
from rdflib.term import URIRef, Literal
from Queries import queryLabel

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
class Crowd:
    # load crowdsource data
    crowdSource = pd.read_csv(r'C:\Users\David\Desktop\Chatbot\Data\crowd_data.tsv', sep='\t')
    # filter out malicious workers by their WorkTimeInSeconds

    workTimeAndApprovalRate = crowdSource
    workTimeAndApprovalRate['LifetimeApprovalRate'] = workTimeAndApprovalRate['LifetimeApprovalRate'].str.replace('%',
                                                                                                                  '').astype(
        float)
    workTimeAndApprovalRate = workTimeAndApprovalRate.loc[workTimeAndApprovalRate['WorkTimeInSeconds'] >= 10]
    # Filter out malicious workers by their LifetimeApprovalRate
    workTimeAndApprovalRate = workTimeAndApprovalRate.loc[workTimeAndApprovalRate['LifetimeApprovalRate'] >= 50]
    aggAns = workTimeAndApprovalRate.groupby('HITId')['AnswerLabel'].agg(pd.Series.mode).to_frame()
    # count number of pros and cons and compute inter-rater rate
    zdf = workTimeAndApprovalRate.filter(['HITId', 'AnswerLabel'])
    numCnt = zdf.groupby('HITId')['AnswerLabel'].value_counts().to_frame()
    counts = zdf.groupby('HITId')['AnswerLabel'].value_counts('counts').to_frame()
    irate = counts.groupby('HITId')['AnswerLabel'].max()
# %%
    def searchInCrowd(self, entity, relation, graph, WDT, WD, cleanedCrowdDataSet, aggAns, numCnt, irate):
        isInCrowd = False
        relid = getRelWDTid(graph, WDT, relation)
        entURI = getEntURI(graph, entity)
        entid = getEntIdByURI(WD, entURI[0])

        rate = 0
        lbl = 0
        lblRev = 0
        incorr = 0
        corr = 0
        corrans = {}
        p_i = 0
        frominput3 = False
        kappa_values = {}
        # check if entity and relation exist in crowd data
        if len(relid) != 0 and len(entid) != 0:
            wdtRelid = 'wdt:{}'.format(relid[0])
            wdtEntid = 'wd:{}'.format(entid)
            # check if entity and relation exist in crowd data
            res1 = cleanedCrowdDataSet[
                (cleanedCrowdDataSet['Input2ID'] == wdtRelid) & (cleanedCrowdDataSet['Input1ID'] == wdtEntid)]
            res2 = cleanedCrowdDataSet[
                (cleanedCrowdDataSet['Input2ID'] == wdtRelid) & (cleanedCrowdDataSet['Input3ID'] == wdtEntid)]

            if not res1.empty or not res2.empty:
                print(res1)
                isInCrowd = True
                for index, row in res1.iterrows():
                    if row["AnswerLabel"] == "CORRECT":
                        corr += 1
                        print("CORRECT", row["AnswerLabel"])
                        if not row["FixValue"] == "" or not row["FixPosition"].isna():
                            if str(row["FixValue"]).startswith("D") or str(row["FixValue"]).startswith("Q"):
                                corrans[row["FixValue"]] = + 1
                            elif row["Input3ID"] != wdtEntid:
                                print("CORRECT", row["Input3ID"])
                                corrans[row["Input3ID"]] = + 1
                                frominput3 = True
                            else:
                                corrans[row["FixPosition"]] = + 1
                    elif row["AnswerLabel"] == "INCORRECT":
                        incorr += 1
                        print("CORRECT", row["AnswerLabel"])
                        if not row["FixValue"] == "" or not row["FixPosition"].isna():
                            corrans[row["FixValue"]] = + 1



                # calc of inter-rater agreement
                batches = cleanedCrowdDataSet['HITTypeId'].unique()
                for batch in batches:
                    corrInBatch = cleanedCrowdDataSet[
                        (cleanedCrowdDataSet.HITTypeId == batch) & (
                                    cleanedCrowdDataSet.AnswerLabel == 'CORRECT')].shape[0]
                    incorrInBatch = cleanedCrowdDataSet[
                        (cleanedCrowdDataSet.HITTypeId == batch) & (
                                    cleanedCrowdDataSet.AnswerLabel == 'INCORRECT')].shape[0]

                n_answer = corrInBatch + incorrInBatch
                p_i = 1 / (n_answer * (n_answer - 1)) * (corrInBatch * (corr - 1) + incorrInBatch * (incorrInBatch - 1))
                print("p_i", p_i)

        # take the answer with the highest number of votes
        nogos = ["I don't understand", "Object", "Subject", "Predicate", "Object", "Predicate", "NaN"]
        corrans = {k: v for k, v in corrans.items() if k not in nogos}
        if frominput3 and incorr > corr:
            corrans = {}
        if len(corrans) > 0:
            corrans = max(corrans, key=corrans.get)
            print("corrans", corrans)
            if corrans.startswith("D") or corrans.startswith("Q"):
                g = set(graph.query("""prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>
    SELECT DISTINCT * WHERE {
      wd:{} rdfs:label ?label . 
      FILTER (langMatches( lang(?label), "en" ) )  
    }""".format(corrans)))

        return isInCrowd, p_i, lbl, corr, lblRev, incorr, corrans


"The executive producer is Sheryl Lee Ralph - according to the crowd, who had an inter-rater agreement of 0.72 in this batch." \
"The answer distribution for this specific task was 2 support votes and 1 reject vote. "

crowd = Crowd()
inCrowd, rate, lbl, cnt1, lblRev, cnt2, corrans = crowd.searchInCrowd('The Princess and the Frog', 'box office', graph,
                                                                      WDT, WD, crowd.workTimeAndApprovalRate,
                                                                      crowd.aggAns, crowd.numCnt, crowd.irate)
if corrans != "":
    answers = corrans
answer_template = "Hi, {} of {} is {}, according to the crowd, who had an inter-rater agreement " \
                  "of {} in this batch; the answer distribution for this task was {} support " \
                  "votes and {} reject vote. ".format(
    'publication date', 'Tom Meets Zizou', answers, rate, cnt1, cnt2)
print(answer_template)

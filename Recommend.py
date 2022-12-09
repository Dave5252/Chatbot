from sklearn.metrics import pairwise_distances
import numpy as np
from LoadData import entity_emb, ent2id, id2ent, lbl2ent, ent2lbl

def recommend(entity):
    # from embeddings gets the nearest neighbours of the entity
    topN = 10
    recomms = []
    if len(entity) > 1:
        int =[]
        for ent in entity:
            emb = np.atleast_2d(entity_emb[ent2id[lbl2ent[ent]]])
            dist = pairwise_distances(emb, entity_emb)
            entRec = []
            for idx in dist.argsort().reshape(-1)[:topN]:
                entRec.append(ent2lbl[id2ent[idx]])
            int.append(entRec)
        # get the intersection of the recommendations
        recomms = list(set(int[0]).intersection(*int[1:]))
    print("recomms: ", recomms)
    # if only one entity is given or the intersection is too small
    if len(entity) == 1 or len(recomms) < 2:
        toTake = 0
        # head + inv(rel) = tail -> inv(rel) = tail - head
        if len(entity) > 1:
            if int[0] > int[1]:
                toTake = 0
            else:
                toTake = 1
        emb = np.atleast_2d(entity_emb[ent2id[lbl2ent[entity[toTake]]]])
        dist = pairwise_distances(emb, entity_emb)
        for idx in dist.argsort().reshape(-1)[:topN]:
            recomms.append(ent2lbl[id2ent[idx]])
    return recomms

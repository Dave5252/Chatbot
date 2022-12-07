from sklearn.metrics import pairwise_distances
import numpy as np
from LoadData import entity_emb, ent2id, id2ent, lbl2ent, ent2lbl

def recommend(entity):
    # from embeddings gets the nearest neighbours of the entity
    topN = 10
    recomms = []
    # take intersection of all  the entities in the embeddings
    if len(entity) > 1:
        int =[]
        for ent in entity:
            emb = np.atleast_2d(entity_emb[ent2id[lbl2ent[ent]]])
            dist = pairwise_distances(emb, entity_emb)
            entRec = []
            for idx in dist.argsort().reshape(-1)[:topN]:
                entRec.append(ent2lbl[id2ent[idx]])
            int.append(set(entRec))
        recomms = set.intersection(*map(set,int))
    # if only one entity is given or the intersection is too small
    elif len(entity) == 1 or len(recomms) < 2:
        # head + inv(rel) = tail -> inv(rel) = tail - head
        emb = np.atleast_2d(entity_emb[ent2id[lbl2ent[entity[0]]]])
        dist = pairwise_distances(emb, entity_emb)
        for idx in dist.argsort().reshape(-1)[:topN]:
            recomms.append(ent2lbl[id2ent[idx]])
    return recomms

from sklearn.metrics import pairwise_distances
import numpy as np
from LoadData import entity_emb, ent2id, id2ent, lbl2ent, ent2lbl

def recommend(entity):
    # from embeddings Nearest Entity Neighbours
    topN = 10
    recomms = []
    emb = np.atleast_2d(entity_emb[ent2id[lbl2ent[entity]]])
    dist = pairwise_distances(emb, entity_emb)
    for idx in dist.argsort().reshape(-1)[:topN]:
        recomms.append(ent2lbl[id2ent[idx]])
    print("normal recomms",recomms)
    return recomms

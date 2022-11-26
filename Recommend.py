from sklearn.metrics import pairwise_distances
import numpy as np
from LoadData import entity_emb, ent2id, id2ent, lbl2ent, ent2lbl
from Queries import *


class Recommendation:
    def __init__(self):
        pass

    # Positive recommendation given film name
    def posRcmFilm(self, entity):
        # TransE
        # from embeddings Nearest Entity Neighbours
        recomms = []
        topN = 10
        emb = np.atleast_2d(entity_emb[ent2id[lbl2ent[entity]]])
        dist = pairwise_distances(emb, entity_emb)
        for idx in dist.argsort().reshape(-1)[:topN]:
            recomms.append(ent2lbl[id2ent[idx]])
        print(recomms)

        return recomms

  #  # TODO: Delete
  #  # positive recommendation given human name and genre
  #  def posRcmHuman(self, entity, target, graph):
  #      # director's movie
  #      rcmds = []
  #      queryFilm = filmGenreTemp.format(entity)
  #      res = set(graph.query(queryFilm))
  #      for row in res:
  #          if target[0] in str(row.genreLbl):
  #              rcmds.append(str(row.movieLbl))
  #      return rcmds
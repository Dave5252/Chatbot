import random
import pandas as pd
from LoadData import entLabelList, relation_emb, entity_emb, ent2id, rel2id, id2ent, ent2lbl, lbl2ent, id2rel
import rdflib
from EntityAndRealtion import *

from Queries import queryLabel, query_template1, query_template2, query_template3
from Recommend import Recommendation
from Multimedia import Multimedia
from HumanOrMovie import humanOrFilm


# from crowd import crowd


class msgP:
    def __init__(self, message):
        self.message = message
        self.entURI = []

    # parse the message and get entity
    def parseEnt(self, graph):
        # Instantiate the entity class
        # classify the message
        entitylist = getEnt(self.message)
        print(entitylist)
        #      if "recommend" not in self.message.lower():
        #          if entitylist[0].startswith('Star Wars'):
        #              newentitylist = " ".join(entitylist)
        #              entitylist = [newentitylist]
        entList = []
        print("entlist:", entitylist)
        for idx, entity in enumerate(entitylist):
            # check if URI exist
            self.entURI = getEntURI(graph, entity)
            # if exist, then append entity label
            if len(self.entURI) != 0:
                print('entURI exist')
                entList.append(entity)
            # if not, then query typo
            else:
                print('entURI does not exist')
        #        entTypoCorr = checkTypo(entLabelList, entity)
        #        print('typo corrected as: ', entTypoCorr)
        #        entTypoURI = getEntURI(graph, entTypoCorr)
        #        print('typoCorr URI: ', entTypoURI)
        #        if len(entTypoURI) != 0:
        #            entList.append(entTypoCorr)
        print(entList)
        return entList

    def parseRel(self, entity, graph, WDT):
        relationList = getRel(self.message)
        print("parseRel", entity, relationList)
        if 'recommend' not in relationList:
            relList = []
            for idx, relation in enumerate(relationList):
                print("relation:", relation)

                relURI = getRelURI(graph, relation, WDT)
                print("relURI: ", relURI)
                if len(relURI) != 0:
                    print('relURI exist')
                    relList.append(relation)
                # if not, then query alias
                else:
                    print('relURI does not exist')
        #               relAliasList = searchAlias(relation, predAlias)
        #              print('Alias is: ', relAliasList)
        #              if len(relAliasList) != 0:
        #                  relList.append(relAliasList[0])
        else:
            relList = ['recommend']
        return relList

        # parse the message and get the response

    def parseMsg(self, graph, WDT, WD, images):
        entities = self.parseEnt(graph)
        relations = self.parseRel(entities, graph, WDT)
        print("parseMsg", entities, relations)
        print(self.message)

        answer_template = "Sorry, there seems no answer to your question. Please try to rephrase or simplify your question."

        # check if there image for the entity
        noPic = 'picture' not in self.message.lower()
        noImage = 'image' not in self.message.lower()
        noPhoto = 'photo' not in self.message.lower()
        noLookLike = 'look like' not in self.message.lower()
        noLooksLike = "looks like" not in self.message.lower()
        notPicture = noPic and noImage and noPhoto and noLookLike and noLooksLike
        print("is not picture", notPicture)

        ## Factual Questions
        # check if one entity, one relation
        if len(entities) == 1 and len(relations) == 1 and 'recommend' not in relations and notPicture:
            print("One ent one rel (Factual Questions)")
            entity = entities[0]
            relation = relations[0]
            #            incrowd, rate, lbl, cnt1, lblRev, cnt2 = checkCrowdER(entity, relation, graph, WDT, WD,
            #                                                                  crowd.cleanCrowd,
            #                                                                  crowd.aggAns, crowd.numCnt, crowd.irate)
            #           print('crowd')
            #           print('crowd, rate, lbl,cnt1,lblRev,cnt2: ', incrowd, rate, lbl, cnt1, lblRev, cnt2)
            relid = getRelWDTid(graph, WDT, relation)
            res = []
            # query with relid and entity label
            if len(relid) != 0:
                query_template = query_template1.format(entity, relid[0])
                res = set(graph.query(query_template))
                print(res, len(res))
            if len(res) == 0:
                # Check if embedding question
                try:
                    embedAnds = self.checkEmbed(graph, WD, WDT, entity, relation)
                    answer_template = f"Here is the answer to your question: {embedAnds}"
                    print("PREFAAIL:", answer_template)
                except:
                    answer_template = "Sorry, there seems no answer to your question. Please try to rephrase or simplify your question."



            else:
                # TODO: maybe delete
                print("What the hell is goin OOOOOOOON res:", res)
                # parse res set into list of strings
                answers = []
                for row in res:
                    # if result is URI then query label
                    if isinstance(row[0], rdflib.term.URIRef):
                        qid = getEntIdByURI(WD, row[0])
                        entLbls = set(graph.query(queryLabel.format(qid)))
                        print(entLbls, len(entLbls))
                        for entlbl in entLbls:
                            answers.append(str(entlbl.label))
                    # if result is not URI, meaning getting number and output directly
                    else:
                        answers.append(str(row.objU))
                #  if incrowd:
                #      answer_template = "Hi, {} of {} is {}, according to the crowd, who had an inter-rater agreement of {} in this batch; the answer distribution for this task was {} support votes and {} reject vote. ".format(
                #          relation, entity, answers, rate, cnt1, cnt2)
                #  else:
                answer_template = "Hi, {} of {} is {}".format(relation, entity, answers)
                print(answer_template)

        # if two entities
        # TODO deleete
        if len(entities) == 2 and notPicture and 'recommend' not in relations:
            print("case2")
            print(entities[1])
            query1 = query_template2.format(entities[0], entities[1])
            query2 = query_template3.format(entities[0], entities[1])
            query3 = query_template2.format(entities[1], entities[0])
            query4 = query_template3.format(entities[1], entities[0])
            res1 = set(graph.query(query1))
            res2 = set(graph.query(query2))
            res3 = set(graph.query(query3))
            res4 = set(graph.query(query4))
            res = set.union(res1, res2, res3, res4)
            print(res, len(res))
            # incrowd, rate, lbl, cnt1, lblRev, cnt2 = checkCrowdER(entities[1], entities[0], graph, WDT, WD,
            #                                                      crowd.cleanCrowd, crowd.aggAns, crowd.numCnt,
            #                                                      crowd.irate)

            if len(res) == 0:
                answer_template = "Sorry, there seems no answer to your question. Please try to rephrase or simplify your question."
                print(answer_template)
            else:
                # parse res set into list of strings
                answers = []
                for row in res:
                    answers.append(str(row.relL))
                #   if incrowd:
                #       answer_template = "Hi, {} of {} is {}, according to the crowd, who had an inter-rater agreement of {} in this batch; the answer distribution for this task was {} support votes and {} reject vote. ".format(
                #           relation, entity, answers, rate, cnt1, cnt2)
                #   else:
                answer_template = "Hi, {} of {} is {}".format(relation, entity, answers)
                print(answer_template)

        # recommendation
        if 'recommend' in relations:
            answer_templates = ['Here are the recommendations: {}, {}, or {}.', 'You may like: {}, {}, or {}.',
                                'I recommend: {}, {}, or {}.']
            rcm = Recommendation()
            entity = entities[0]

            # TODO delete tis shi

            #        # from  Tutorial: Using Pretrained Transformer Architectures
            #        sentiment_pipeline = pipeline('text-classification',
            #                                      model='distilbert-base-uncased-finetuned-sst-2-english')
            #        label = sentiment_pipeline(self.message)[0]['label']
            #
            rcmds = rcm.posRcmFilm(entity)
            answer_template = answer_templates[random.randint(0, len(answer_templates) - 1)].format(
                rcmds.pop(random.randint(0, len(rcmds) - 1)), rcmds.pop(random.randint(0, len(rcmds) - 1)),
                rcmds.pop(random.randint(0, len(rcmds) - 1)))
            print(answer_template)

        # Image Question
        if not notPicture:
            mutli_m = Multimedia()
            print("Show Pictures")
            #       if not noPoster:
            #           if len(entities) != 0:
            #               entity = entities[0]
            #               human, film = humanOrFilm(graph, entity)
            #               if human:
            #                   answer_template = "Only movie has poster, please reinput."
            #               elif film:
            #                   print("Show Poster")
            #                   imgids = mutli_m.showPoster(entity, graph, images)
            #                   print(imgids)
            #                   if len(imgids) > 0:
            #                       answer_template = imgids[0]
            #                   else:
            #                       answer_template = "Sorry, I can't find the picture you requested."
            #           elif len(entities) == 0:
            #               # return poster of random movie genre
            #               tokens = getTokens(self.message)
            #               genre = returnNounBfMovie(tokens)
            #               imgid = mutli_m.showGenrePoster(graph, images, genre)
            #               print(imgid)
            #               answer_template = imgid

            if not noPic or not noImage or not noPhoto or not noLookLike or not noLooksLike:
                print("Show pic or image")
                if len(entities) != 0:
                    entity = entities[0]
                    human, film = humanOrFilm(graph, entity)

                    if human:
                        print("Show picture related to human")
                        imgids = mutli_m.showPicwHumanInp(entity, graph, images)
                        print("imgids ", imgids)
                        if len(imgids) > 0:
                            answer_template = imgids[0]
                        else:
                            answer_template = "Sorry, I can't find the picture you requested."
                    elif film:
                        print("Show picture related to film")
                        imgids = mutli_m.showPicwFilmInp(entity, graph, images)
                        # print(imgids)
                        if len(imgids) > 0:
                            answer_template = imgids[0]
                        else:
                            answer_template = "Sorry, I can't find the picture you requested."
                        print(answer_template)

                elif len(entities) == 0:
                    # return pic of random movie genre
                    tokens = getTokens(self.message)
                    genre = returnNounBfMovie(tokens)
                    imgid = mutli_m.showGenrePoster(graph, images, genre)
                    print(imgid)
                    answer_template = "Hi, this is the poster you requested.{}".format(imgid)

        return answer_template

    # Function to extract relation
    def checkEmbed(self, graph, WD, WDT, entity, relation):
        print("Embedding")
        head = entity_emb[ent2id[lbl2ent[entity]]]
        # "occupation" relation
        relwdtids = getRelWDTid(graph, WDT, relation)
        print("relwdtids", relwdtids)
        pred = relation_emb[rel2id[WDT[relwdtids[0]]]]
        # add vectors according to TransE scoring function.
        lhs = head + pred
        # compute distance to *any* entity
        dist = pairwise_distances(lhs.reshape(1, -1), entity_emb).reshape(-1)
        # find most plausible entities
        most_likely = dist.argsort()
        # compute ranks of entities
        ranks = dist.argsort().argsort()
        ans = pd.DataFrame([
            (id2ent[idx][len(WD):], ent2lbl[id2ent[idx]], dist[idx], rank + 1)
            for rank, idx in enumerate(most_likely[:10])],
            columns=('Entity', 'Label', 'Score', 'Rank'))
        print("EMBEDDINGS WORKED MY DUDE")
        return list(ans['Label'])

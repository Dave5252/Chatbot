import random

from LoadData import relation_emb, entity_emb, ent2id, rel2id, id2ent, ent2lbl, lbl2ent
import rdflib
from EntityAndRealtion import *

from Queries import queryLabel, query_template1, query_template2, query_template3
from Recommend import *
from Multimedia import Multimedia
from Crowd import *


# from crowd import crowd


class msgP:
    def __init__(self, message):
        # can not find entities with "-", needs to  be:  "–"
        if "-" in message:
            message = message.replace("-", "–")
        self.message = message
        self.entURI = []

    # parse the message and get the response
    def parseMsg(self, graph, WDT, WD, images):
        entities = self.parseEnt(graph)
        rels = self.parseRel(entities, graph, WDT)
        print("parseMsg", entities, rels)
        print(self.message)
        # initiate fail answer template
        answer_template = "Sorry, there is no answer to your question. Please try to rephrase or simplify your question."

        # check if there image for the entity
        noPic = 'picture' not in self.message.lower()
        noImage = 'image' not in self.message.lower()
        noPhoto = 'photo' not in self.message.lower()
        noLookLike = 'look like' not in self.message.lower()
        noLooksLike = "looks like" not in self.message.lower()
        notPicture = noPic and noImage and noPhoto and noLookLike and noLooksLike
        print("is not picture", notPicture)

        # check if one entity, one relation
        if len(entities) == 1 and len(rels) == 1 and 'recommend' not in rels and notPicture:
            print("One ent one rel (Factual Questions)")
            entity = entities[0]
            relation = rels[0]
            crowd = Crowd()
            inCrowd, rate, lbl, cnt1, lblRev, cnt2 = crowd.checkCrowdER(entity, relation, graph, WDT, WD,
                                                                        crowd.cleanData, Crowd.aggAns, crowd.numCnt,
                                                                        crowd.irate)
            print('crowd')
            print('crowd, rate, lbl,cnt1,lblRev,cnt2: ', inCrowd, rate, lbl, cnt1, lblRev, cnt2)
            relid = getRelWDTid(graph, WDT, relation)
            res = []
            # query with relid and entity label
            if len(relid) == 1:
                query_template = query_template1.format(entity, relid[0])
                res = set(graph.query(query_template))
                print(res, len(res))
                answers = []
                for row in res:
                    ##if result is URI then query label
                    if isinstance(row[0], rdflib.term.URIRef):
                        qid = getEntIdByURI(WD, row[0])
                        entLbls = set(graph.query(queryLabel.format(qid)))
                        print("entLbls",entLbls, len(entLbls))
                        for entlbl in entLbls:
                            answers.append(str(entlbl.label))
                    # if result is not URI, meaning getting number and output directly
                    else:
                        answers.append(str(row.objU))
                    answer_template = "Hi, the {} of {} is {}".format(relation, entity, answers[0])
                    if len(answers) > 1:
                        # more than one answer --> use embedding. Not the nicest way to do it
                        res = []
                if inCrowd and answers != []:
                    answer_template = "Hi, {} of {} is {}, according to the crowd, who had an inter-rater agreement " \
                                      "of {} in this batch; the answer distribution for this task was {} support " \
                                      "votes and {} reject vote. ".format(
                        relation, entity, answers[0], rate, cnt1, cnt2)

            if len(res) == 0 and inCrowd == False:
                # Check if embedding question
                try:
                    embedAnds = self.checkEmbed(graph, WD, WDT, entity, relation)
                    # return the first answer
                    counter = 0
                    for element in embedAnds:
                        if counter == 0:
                            answer_template = "Hi, the {} of {} is {}. ".format(relation, entity, element)
                            counter += 1
                        elif counter < 4:
                            answer_template += "Another answer is {}. ".format(element)
                            counter += 1
                    # answer_template = f"Here is the answer to your question: {embedAnds[0]}"
                    print("PREFAAIL:", answer_template)
                except:
                    answer_template = "Sorry, there is no answer to your question. Please try to rephrase or simplify your question."


        # if two entities
        # TODO deleete
        if len(entities) == 2 and notPicture and 'recommend' not in rels:
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
            # inCrowd, rate, lbl, cnt1, lblRev, cnt2 = checkCrowdER(entities[1], entities[0], graph, WDT, WD,
            #                                                      crowd.cleanCrowd, crowd.aggAns, crowd.numCnt,
            #                                                      crowd.irate)

            if len(res) == 0:
                answer_template = "Sorry, there is no answer to your question. Please try to rephrase or simplify your question."
                print(answer_template)
            else:
                # parse res set into list of strings
                answers = []
                for row in res:
                    answers.append(str(row.relL))
                #   if inCrowd:
                #       answer_template = "Hi, {} of {} is {}, according to the crowd, who had an inter-rater agreement of {} in this batch; the answer distribution for this task was {} support votes and {} reject vote. ".format(
                #           relation, entity, answers, rate, cnt1, cnt2)
                #   else:
                answer_template = "Hi, {} of {} is {}".format(relation, entity, answers)
                print(answer_template)

        # recommendation
        if 'recommend' in rels:
            answer_templates = ['Here are the recommendations: {}, {}, or {}.', 'You may like: {}, {}, or {}.',
                                'I recommend: {}, {}, or {}.']
            rcmds = recommend(entities)
            rcmds = [rcmd for rcmd in rcmds if rcmd not in entities]
            answer_template = answer_templates[random.randint(0, len(answer_templates) - 1)].format(
                rcmds.pop(random.randint(0, len(rcmds) - 1)), rcmds.pop(random.randint(0, len(rcmds) - 1)),
                rcmds.pop(random.randint(0, len(rcmds) - 1)))
            print(answer_template)

        # Image Question
        if not notPicture:
            mutli_m = Multimedia()
            print("Show Pictures")
            if not noPic or not noImage or not noPhoto or not noLookLike or not noLooksLike:
                if len(entities) != 0:
                    entity = entities[0]
                    imgageids = mutli_m.showPicOfHuman(entity, graph, images)
                    print("imgageids ", imgageids)
                    if len(imgageids) > 0:
                        answer_template = imgageids[0]
        return answer_template

    # Function to extract relation (Embeddings for the DDIS Movie Graph)
    def checkEmbed(self, graph, WD, WDT, entity, relation):
        head = entity_emb[ent2id[lbl2ent[entity]]]
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
    # parse the message and get entity
    def parseEnt(self, graph):
        # classify the message
        entitylist = getEnt(self.message)
        entList = []
        print("Entity list:", entitylist)
        for entity in entitylist:
            # check if URI exist
            self.entURI = getEntURI(graph, entity)
            # if exist, then append entity label
            if len(self.entURI) != 0:
                print('entURI exist')
                entList.append(entity)
            # if not, then query typo
            else:
                print('entURI does not exist')
        print(entList)
        return entList


    # parse the relation
    def parseRel(self, entity, graph, WDT):
        relationList = getRel(self.message)
        print("parseRel", entity, relationList)
        if 'recommend' not in relationList:
            relationListToReturn = []
            for relation in relationList:
                print("relation:", relation)
                relURI = getRelURI(graph, relation, WDT)
                if len(relURI) != 0:
                    relationListToReturn.append(relation)
                # if not, then query alias
                else:
                    print('relURI does not exist')

        else:
            relationListToReturn = ['recommend']
        return relationListToReturn
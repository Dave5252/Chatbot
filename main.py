import random

from LoadData import relation_emb, entity_emb, ent2id, rel2id, id2ent, ent2lbl, lbl2ent
import rdflib
from EntityAndRealtion import *

from Queries import queryLabel, queryOneRelOneEnt, query_template2, query_template3
from Recommend import *
from Multimedia import Multimedia
from Crowd import *


# from crowd import crowd


class msgP:
    def __init__(self, message):
        self.message = message
        self.entURI = []

    # parse the message and get the response
    def parseMsg(self, graph, WDT, WD, images):
        entities = self.parseEnt(graph, WD)
        rels = self.parseRel(entities, graph, WDT)
        print("parseMsg", entities, rels)
        print(self.message)
        # initiate fail answer template
        answer_template = "Sorry, there is no answer to your question. Please try to rephrase or simplify your question. Keep in mind the SPARQL queries are case sensitive (Surname Name) aswell as (Movies)."

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
            inCrowd, rate, lbl, cnt1, lblRev, cnt2, corrans = crowd.searchInCrowd(entity, relation, graph, WDT, WD,
                                                                         crowd.workTimeAndApprovalRate, Crowd.aggAns, crowd.numCnt,
                                                                         crowd.irate)
            print('crowd, rate, lbl,cnt1,lblRev,cnt2: ', inCrowd, rate, lbl, cnt1, lblRev, cnt2)
            relid = getRelWDTid(graph, WDT, relation)
            result = []
            # query with relid and entity label
            print("relid", relid)
            if len(relid) == 1:
                query_template = queryOneRelOneEnt.format(entity, relid[0])
                print("query_template", query_template)
                result = set(graph.query(query_template))
                print("Query result",result, len(result))
                answers = []
                for res in result:
                    # if result is URI then query label
                    if isinstance(res[0], rdflib.term.URIRef):
                        qid = getEntIdByURI(WD, res[0])
                        entLbls = set(graph.query(queryLabel.format(qid)))
                        print("entLbls",entLbls, len(entLbls))
                        for entlbl in entLbls:
                            answers.append(str(entlbl.label))
                    # if result is not URI, meaning getting number and output directly
                    else:
                        print("take number out, res.objU", res.objU)
                        answers.append(str(res.objU))
                    answer_template = "Hi, the {} of {} is {}".format(relation, entity, answers[0])
                    if len(answers) > 1:
                        # more than one answer --> use embedding. Not the nicest way to do it
                        result = []
                if inCrowd:
                    if corrans != "":
                        answers = corrans
                    if type(answers) == list:
                        answers = answers[0]
                    answer_template = "Hi, {} of {} is {}, according to the crowd, who had an inter-rater agreement " \
                                      "of {} in this batch; the answer distribution for this task was {} support " \
                                      "votes and {} reject vote. ".format(
                        relation, entity, answers, rate, cnt1, cnt2)

            if len(result) == 0 and inCrowd == False:
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
                            answer_template += "I also found the following answer: {}. ".format(element)
                            counter += 1
                    # answer_template = f"Here is the answer to your question: {embedAnds[0]}"
                    print("PREFAAIL:", answer_template)
                except:
                    answer_template = "Sorry, there is no answer to your question. Please try to rephrase or simplify your question. Keep in mind the SPARQL queries are case sensitive (Surname Name) oaswell as (Movies)."

        # recommendation
        if 'recommend' in rels:
            answer_templates = ['Here are the recommendations: {}, {}, or {}.', 'You may like: {}, {}, or {}.',
                                'I recommend: {}, {}, or {}.']
            rcmds = recommend(entities)
            rcmds = [rcmd for rcmd in rcmds if rcmd not in entities]
            if len(rcmds) >= 3:
                answer_template = answer_templates[random.randint(0, len(answer_templates) - 1)].format(
                    rcmds.pop(random.randint(0, len(rcmds) - 1)), rcmds.pop(random.randint(0, len(rcmds) - 1)),
                    rcmds.pop(random.randint(0, len(rcmds) - 1)))
            elif len(rcmds) == 2:
                answer_template = "Here are some recommendations for you: {} or {}".format(rcmds[0], rcmds[1])
            elif len(rcmds) == 1:
                answer_template = "Here is a recommendation: {}".format(rcmds[0])
            else:
                answer_template = "Sorry, there is no recommendation for you."
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
        if len(entities) >=1 and len(rels) >= 1 and answer_template == "Sorry, there is no answer to your question. Please try to rephrase or simplify your question. Keep in mind the SPARQL queries are case sensitive (Surname Name) aswell as (Movies).":
            print("More than one entity and more than one relation")
            [entities.remove(entity) for entity in entities if entity in rels]
            for entity in entities:
                print("first try & entities", entities)
                try:
                    print("entity", entity)
                    print("rels", rels)
                    embedAnds = self.checkEmbed(graph, WD, WDT, entity, rels[0])
                    # return the first answer
                    print("embedAnds of fix", embedAnds)
                    counter = 0
                    for element in embedAnds:
                        if counter == 0:
                            answer_template = "Hi, the {} of {} is {}. ".format(rels, entity, element)
                            counter += 1
                        elif counter < 4:
                            answer_template += "I also found the following answer: {}. ".format(element)
                            counter += 1
                    # answer_template = f"Here is the answer to your question: {embedAnds[0]}"
                    print("PREFAAIL:", answer_template)
                except:
                    answer_template = "Sorry, there is no answer to your question. Please try to rephrase or simplify your question. Keep in mind the SPARQL queries are case sensitive (Surname Name) oaswell as (Movies)."

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
    def parseEnt(self, graph, WD):
        """
        Parse the message and get entity
        :param graph: graph
        :param WD: wikidata
        :return: entity list
        """
        # classify the message
        entitylist = getEnt(self.message)
        entList = []
        print("Entity list:", entitylist)
        for entity in entitylist:
            # check if URI exist
            self.entURI = getEntURI(graph, entity)
            # if entity exist, then append entity label
            if len(self.entURI) != 0:
                print('entURI exist', self.entURI)
                [entList.append(str(ent.label)) for ent in set(graph.query(queryLabel.format(getEntIdByURI(WD, self.entURI[0]))))]
            # if not, then query typo
            else:
                # can not find entities with "-", needs to  be:  "–"
                if "-" in self.message:
                    entity = entity.replace("-", "–")
                    self.entURI = getEntURI(graph, entity)
                    # if exist, then append entity label
                    if len(self.entURI) != 0:
                        print('entURI exist')
                        [entList.append(str(ent.label)) for ent in set(graph.query(queryLabel.format(getEntIdByURI(WD, self.entURI[0]))))]
                elif "–" in self.message:
                    entity = entity.replace("–", "-")
                    self.entURI = getEntURI(graph, entity)
                    # if exist, then append entity label
                    if len(self.entURI) != 0:
                        print('entURI exist')
                        [entList.append(str(ent.label)) for ent in set(graph.query(queryLabel.format(getEntIdByURI(WD, self.entURI[0]))))]
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
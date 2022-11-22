from loadData import entLabelList
import rdflib
from EntityAndRealtion import *

from Queries import queryLabel, query_template1, query_template2, query_template3
from Recommend import Recommendation
from Multimedia import Multimedia
from transformers import pipeline
from HumanOrMovie import humanOrFilm
from loadData import entLabelList  #, predAlias
#from crowd import crowd
from Crowd import checkCrowdER


class msgP:
    def __init__(self, message):
        self.message = message

    # parse the message and get entity
    def parseEnt(self, graph):
        # Instantiate the entity class
        # classify the message
        entitylist = getEnt(self.message)
        print(entitylist)
        entList = []
        for idx, entity in enumerate(entitylist):
            # check if URI exist
            entURI = getEntURI(graph, entity)
            print("entURI:", entURI)
            # if exist, then append entity label
            if len(entURI) != 0:
                print('entURI exist')
                entList.append(entity)
            # if not, then query typo
            else:
                print('entURI does not exist')
                entTypoCorr = checkTypo(entLabelList, entity)
                print('typo corrected as: ', entTypoCorr)
                entTypoURI = getEntURI(graph, entTypoCorr)
                print('typoCorr URI: ', entTypoURI)
                if len(entTypoURI) != 0:
                    entList.append(entTypoCorr)
        print(entList)
        return entList

    def parseRel(self, entity, graph, WDT):
        relationList, tbd = getRel(self.message)
        print("parseRel", entity, relationList, tbd)
        if tbd == True:
            relationList = tbdRel(relationList)
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

        answer_template = "Sorry, there seems no answer to your question. Please try to rephrase or simplify your question."

        # for showing images
        noPic = 'picture' not in self.message.lower()
        noFrame = 'frame' not in self.message.lower()
        noPoster = 'poster' not in self.message.lower()
        noImage = 'image' not in self.message.lower()
        notPicture = noPic and noFrame and noPoster and noImage

        # fact-oriented questions
        # if one entity, one relation
        if len(entities) == 1 and len(relations) == 1 and 'recommend' not in relations and notPicture:
            print("case1")
            entity = entities[0]
            relation = relations[0]
#            incrowd, rate, lbl, cnt1, lblRev, cnt2 = checkCrowdER(entity, relation, graph, WDT, WD,
#                                                                  crowd.cleanCrowd,
#                                                                  crowd.aggAns, crowd.numCnt, crowd.irate)
#           print('crowd')
#           print('crowd, rate, lbl,cnt1,lblRev,cnt2: ', incrowd, rate, lbl, cnt1, lblRev, cnt2)
            print(entity, relation)
            relid = getRelWDTid(graph, WDT, relation)
            res = []
            # query with relid and entity label
            if len(relid) != 0:
                query_template = query_template1.format(entity, relid[0])
                res = set(graph.query(query_template))
                print(res, len(res))

            if len(res) == 0:
                answer_template = "Sorry, there seems no answer to your question. Please try to rephrase or simplify your question."
                print(answer_template)
            else:
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
        if len(entities) == 2 and notPicture:
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
            #incrowd, rate, lbl, cnt1, lblRev, cnt2 = checkCrowdER(entities[1], entities[0], graph, WDT, WD,
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
        if 'recommend' in relations and len(entities) == 1:
            rcm = Recommendation()
            rcmds = []
            entity = entities[0]
            sentiment_pipeline = pipeline('text-classification',
                                          model='distilbert-base-uncased-finetuned-sst-2-english')
            label = sentiment_pipeline(self.message)[0]['label']

            human, film = humanOrFilm(graph, entity)

            if human:
                pos_tokens = getTokens(self.message)
                target = returnNAfRcmd(pos_tokens)
                if label == 'POSITIVE':
                    print("ishuman,positive,target is: ", target)
                    rcmds = rcm.posRcmHuman(entity, target, graph)
                elif label == 'NEGATIVE':
                    print("ishuman,negative,target is: ", target)
                #     rcmds = rcm.negRcmHuman(entity,target)
            if film:
                if label == 'POSITIVE':
                    print("isfilm,positive")
                    rcmds = rcm.posRcmFilm(entity)
                elif label == 'NEGATIVE':
                    print("isfilm,negative")
                    # rcmds = rcm.negRcmFilm(entity)

            answer_template = 'Here are the recommendations {}'.format(rcmds)
            print(answer_template)

        # show picture
        if not notPicture:
            mutliM = Multimedia()
            print("Show Pictures")
            if not noPoster:
                # assume here return movie pic
                if len(entities) != 0:
                    entity = entities[0]
                    human, film = humanOrFilm(graph, entity)
                    if human:
                        answer_template = "Only movie has poster, please reinput."
                    elif film:
                        print("Show Poster")
                        imgids = mutliM.showPoster(entity, graph, images)
                        print(imgids)
                        if len(imgids) > 0:
                            answer_template = "Hi, this is the poster you requested.{}".format(imgids[0])
                        else:
                            answer_template = "Sorry, I can't find the picture you requested."
                elif len(entities) == 0:
                    # return poster of random movie genre
                    tokens = getTokens(self.message)
                    genre = returnNounBfMovie(tokens)
                    imgid = mutliM.showGenrePoster(graph, images, genre)
                    print(imgid)
                    answer_template = "Hi, this is the poster you requested.{}".format(imgid)

            elif not noPic or not noImage:
                # assume here return human pic
                print("Show pic or image")
                if len(entities) != 0:
                    entity = entities[0]
                    human, film = humanOrFilm(graph, entity)

                    if human:
                        print("Show picture related to human")
                        imgids = mutliM.showPicwHumanInp(entity, graph, images)
                        print(imgids)
                        if len(imgids) > 0:
                            answer_template = "Hi, this is the picture you requested.{}".format(imgids[0])
                        else:
                            answer_template = "Sorry, I can't find the picture you requested."
                    elif film:
                        print("Show picture related to film")
                        imgids = mutliM.showPicwFilmInp(entity, graph, images)
                        # print(imgids)
                        if len(imgids) > 0:
                            answer_template = "Hi, this is the picture you requested.{}".format(imgids[0])
                        else:
                            answer_template = "Sorry, I can't find the picture you requested."
                        print(answer_template)

                elif len(entities) == 0:
                    # return pic of random movie genre
                    tokens = getTokens(self.message)
                    genre = returnNounBfMovie(tokens)
                    imgid = mutliM.showGenrePoster(graph, images, genre)
                    print(imgid)
                    answer_template = "Hi, this is the poster you requested.{}".format(imgid)

            elif not noFrame:
                print("Show frame")
                answer_template = "Hi, this is the frame you requested.{}".format(imgids)

        return answer_template

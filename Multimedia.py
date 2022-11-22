# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 14:58:00 2021

@author: Wenqing
"""
### This file deals with all questions that is multimedia related

from Queries import imdbIdTemp, genrePosterTemp, movie2ActorImdbTemp, humanImdbIdTemp


class Multimedia:
    def __init__(self):
        pass

    # show poster of movie
    def showPoster(self, entity, graph, images):
        queryImdb = imdbIdTemp.format(entity)

        res = list(graph.query(queryImdb))

        imdbIds = []
        for idx, row in enumerate(res):
            imdbId = str(res[idx][0])
            imdbIds.append(imdbId)
        filmsList = []
        for idx, imdbid in enumerate(imdbIds):
            films = list(filter(lambda film: film['movie'] == [imdbid] and film['type'] == 'poster', images))

            filmsList += films
        print(filmsList)
        imgids = []
        for idx, film in enumerate(filmsList):
            imgid = film['img']
            imgids.append('image:' + imgid.strip('.jpg'))
        return imgids

    # show poster of movie in certain genre
    def showGenrePoster(self, graph, images, genre):
        queryGenre = genrePosterTemp.format(genre)
        res = list(graph.query(queryGenre))

        imdbIds = []
        for idx, row in enumerate(res):
            imdbId = str(res[idx][0])
            imdbIds.append(imdbId)

        for idx, imdbid in enumerate(imdbIds):
            films = list(filter(lambda film: film['movie'] == [imdbid] and film['type'] == 'poster', images))
            if len(films) != 0:
                break
        print(films)
        imgids = []
        for idx, film in enumerate(films):
            imgid = film['img']
            imgids.append('image:' + imgid.strip('.jpg'))
        imgid = imgids[0]
        return imgid

    # show picture given human name as entity
    def showPicwHumanInp(self, entity, graph, images):
        # query film and get imdbid of human
        queryImdbHuman = humanImdbIdTemp.format(entity)
        res = list(graph.query(queryImdbHuman))
        # print(res,len(res))

        imdbIds = []
        for idx, row in enumerate(res):
            imdbId = str(res[idx][0])
            if imdbId.startswith('nm'):
                imdbIds.append(imdbId)
        print(imdbIds)
        filmsList = []
        for idx, imdbid in enumerate(imdbIds):
            films = list(filter(lambda film: film['cast'] == [imdbid], images))
            filmsList += films
        # print(filmsList)
        imgids = []
        for idx, film in enumerate(filmsList):
            imgid = film['img']
            imgids.append('image:' + imgid.strip('.jpg'))
        print(imgids)

        return imgid

    # show picture given film name as entiy
    def showPicwFilmInp(self, entity, graph, images):
        # query film and get imdbid of human
        queryImdbActor = movie2ActorImdbTemp.format(entity)
        res = list(graph.query(queryImdbActor))
        # print(res,len(res))

        imdbIds = []
        for idx, row in enumerate(res):
            imdbId = str(res[idx][0])
            if imdbId.startswith('nm'):
                imdbIds.append(imdbId)
        print(imdbIds)
        filmsList = []
        for idx, imdbid in enumerate(imdbIds):
            films = list(filter(lambda film: film['cast'] == [imdbid], images))
            if len(films) != 0:
                filmsList = films
                break
        # print(filmsList)
        imgids = []
        for idx, film in enumerate(filmsList):
            imgid = film['img']
            imgids.append('image:' + imgid.strip('.jpg'))
        print(imgids)
        return imgids

    # def showFrameWFilmInp(self,entity,graph,images):

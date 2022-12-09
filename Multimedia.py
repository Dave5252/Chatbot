from Queries import humanImdbIdTemp


class Multimedia:
    # show picture given human name as entity
    def showPicOfHuman(self, entity, graph, images):
        # query film and get imdbid of human
        queryImdbHuman = humanImdbIdTemp.format(entity)
        res = list(graph.query(queryImdbHuman))
        imdbIds = []
        for idx, row in enumerate(res):
            imdbId = str(res[idx][0])
            if imdbId.startswith('nm'):
                imdbIds.append(imdbId)
        filmsList = []
        print("imdb ids",imdbIds)
        for imdbid in imdbIds:
            movies = list(filter(lambda film: film['cast'] == [imdbid], images))
            filmsList += movies
        imgids = []
        for film in filmsList:
            imgid = film['img']
            imgids.append('image:' + imgid.strip('.jpg'))

        return imgids
from Queries import humanImdbIdTemp


class Multimedia:
    def __init__(self):
        pass

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
        print(imdbIds)
        for idx, imdbid in enumerate(imdbIds):
            films = list(filter(lambda film: film['cast'] == [imdbid], images))
            filmsList += films
        imgids = []
        for idx, film in enumerate(filmsList):
            imgid = film['img']
            imgids.append('image:' + imgid.strip('.jpg'))
        print(imgids)

        return imgids
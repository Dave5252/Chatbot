
class msgP:
    def __init__(self, message):
        self.message = message

    ## parse the message and get entity
    def parseEnt(self, graph):
        ge = getEntity()
        entityList = ge.getEnt(self.message)
        print(entityList)
        entList = []
        for idx, entity in enumerate(entityList):
            # check if URI exist
            entURI = ge.getEntURI(graph, entity)
            print("entURI:", entURI)
            # if exist, then append entity label
            if len(entURI) != 0:
                print('entURI exist')
                entList.append(entity)
            # if not, then query typo
            else:
                print('entURI does not exist')
                entTypoCorr = ge.checkTypo(entLblList, entity)
                print('typo corrected as: ', entTypoCorr)
                entTypoURI = ge.getEntURI(graph, entTypoCorr)
                print('typoCorr URI: ', entTypoURI)
                if len(entTypoURI) != 0:
                    entList.append(entTypoCorr)
        print(entList)
        return entList
    def parseMsg(self):

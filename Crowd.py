from EntityAndRealtion import *
import pandas as pd
class Crowd:
    # load crowdsource data
    crowdSource = pd.read_csv(r'C:\Users\David\Desktop\Chatbot\Data\crowd_data.tsv', sep='\t')
    # filter out malicious workers by their WorkTimeInSeconds

    workTimeAndApprovalRate = crowdSource
    workTimeAndApprovalRate['LifetimeApprovalRate'] = workTimeAndApprovalRate['LifetimeApprovalRate'].str.replace('%',
                                                                                                                  '').astype(
        float)
    workTimeAndApprovalRate = workTimeAndApprovalRate.loc[workTimeAndApprovalRate['WorkTimeInSeconds'] >= 10]
    # Filter out malicious workers by their LifetimeApprovalRate
    workTimeAndApprovalRate = workTimeAndApprovalRate.loc[workTimeAndApprovalRate['LifetimeApprovalRate'] >= 50]
    aggAns = workTimeAndApprovalRate.groupby('HITId')['AnswerLabel'].agg(pd.Series.mode).to_frame()
    # count number of pros and cons and compute inter-rater rate
    zdf = workTimeAndApprovalRate.filter(['HITId', 'AnswerLabel'])
    numCnt = zdf.groupby('HITId')['AnswerLabel'].value_counts().to_frame()
    counts = zdf.groupby('HITId')['AnswerLabel'].value_counts('counts').to_frame()
    irate = counts.groupby('HITId')['AnswerLabel'].max()

    def searchInCrowd(self, entity, relation, graph, WDT, WD, cleanedCrowdDataSet, aggAns, numCnt, irate):
        isInCrowd = False
        relid = getRelWDTid(graph, WDT, relation)
        entURI = getEntURI(graph, entity)
        entid = getEntIdByURI(WD, entURI[0])

        rate = 0
        lbl = 0
        lblRev = 0
        incorr = 0
        corr = 0
        corrans = {}
        p_i = 0
        frominput3 = False
        kappa_values = {}
        # check if entity and relation exist in crowd data
        if len(relid) != 0 and len(entid) != 0:
            wdtRelid = 'wdt:{}'.format(relid[0])
            wdtEntid = 'wd:{}'.format(entid)
            # check if entity and relation exist in crowd data
            res1 = cleanedCrowdDataSet[
                (cleanedCrowdDataSet['Input2ID'] == wdtRelid) & (cleanedCrowdDataSet['Input1ID'] == wdtEntid)]
            res2 = cleanedCrowdDataSet[
                (cleanedCrowdDataSet['Input2ID'] == wdtRelid) & (cleanedCrowdDataSet['Input3ID'] == wdtEntid)]

            if not res1.empty or not res2.empty:
                print(res1)
                isInCrowd = True
                for index, row in res1.iterrows():
                    if row["AnswerLabel"] == "CORRECT":
                        corr += 1
                        print("CORRECT", row["AnswerLabel"])
                        if not row["FixValue"] == "" or not row["FixPosition"].isna():
                            if str(row["FixValue"]).startswith("D") or str(row["FixValue"]).startswith("Q"):
                                corrans[row["FixValue"]] = + 1
                            elif row["Input3ID"] != wdtEntid:
                                print("CORRECT", row["Input3ID"])
                                corrans[row["Input3ID"]] = + 1
                                frominput3 = True
                            else:
                                corrans[row["FixPosition"]] = + 1
                    elif row["AnswerLabel"] == "INCORRECT":
                        incorr += 1
                        print("CORRECT", row["AnswerLabel"])
                        if not row["FixValue"] == "" or not row["FixPosition"].isna():
                            corrans[row["FixValue"]] = + 1

                # calc of inter-rater agreement
                batches = cleanedCrowdDataSet['HITTypeId'].unique()
                for batch in batches:
                    corrInBatch = cleanedCrowdDataSet[
                        (cleanedCrowdDataSet.HITTypeId == batch) & (
                                cleanedCrowdDataSet.AnswerLabel == 'CORRECT')].shape[0]
                    incorrInBatch = cleanedCrowdDataSet[
                        (cleanedCrowdDataSet.HITTypeId == batch) & (
                                cleanedCrowdDataSet.AnswerLabel == 'INCORRECT')].shape[0]

                n_answer = corrInBatch + incorrInBatch
                p_i = 1 / (n_answer * (n_answer - 1)) * (corrInBatch * (corr - 1) + incorrInBatch * (incorrInBatch - 1))
                print("p_i", p_i)

        # take the answer with the highest number of votes
        nogos = ["I don't understand", "Object", "Subject", "Predicate", "Object", "Predicate", "NaN"]
        corrans = {k: v for k, v in corrans.items() if k not in nogos}
        if frominput3 and incorr > corr:
            corrans = {}
        if len(corrans) > 0:
            corrans = max(corrans, key=corrans.get)
            print("corrans", corrans)
            if corrans.startswith("D") or corrans.startswith("Q"):
                g = set(graph.query("""prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix wd: <http://www.wikidata.org/entity/>
    SELECT DISTINCT * WHERE {
      wd:Q181900 rdfs:label ?label . 
      FILTER (langMatches( lang(?label), "en" ) )  
    }"""))

        return isInCrowd, p_i, lbl, corr, lblRev, incorr, corrans
#class Crowd:
#    # load crowdsource data
#    crowdSource = pd.read_csv(r'C:\Users\David\Desktop\Chatbot\Data\crowd_data.tsv', sep='\t')
#    # filter out malicious workers by their WorkTimeInSeconds
#
#    workTimeAndApprovalRate = crowdSource
#    # workTimeAndApprovalRate = crowdSource.filter(['HITId', 'WorkTimeInSeconds', 'WorkerId', 'LifetimeApprovalRate'], axis=1)
#    workTimeAndApprovalRate['LifetimeApprovalRate'] = workTimeAndApprovalRate['LifetimeApprovalRate'].str.replace('%',
#                                                                                                                  '').astype(
#        float)
#    workTimeAndApprovalRate = workTimeAndApprovalRate.loc[workTimeAndApprovalRate['WorkTimeInSeconds'] > 10]
#    # Filter out malicious workers by their LifetimeApprovalRate
#    workTimeAndApprovalRate = workTimeAndApprovalRate.loc[workTimeAndApprovalRate['LifetimeApprovalRate'] > 50]
#
#    #  maliWorkers = malHits['WorkerId'].unique()
#    #  cleanData = crowdSource
#    #  for malWk in maliWorkers:
#    #      # drop all malicious workers from the crowd data
#    #      cleanedData = cleanData.drop(cleanData[(cleanData['WorkerId'] == malWk)].index)
#    #  # drop all HITs that have low rating
#    #  maliWorkers = malAllTimeRat['WorkerId'].unique()
#    #  cleanData2 = cleanedData
#    #  for malWk in maliWorkers:
#    #      # drop all malicious workers from the crowd data
#    #      cleanedDataFinal = cleanData2.drop(cleanData2[(cleanData2['WorkerId'] == malWk)].index)
#    # aggregate worker answers and get the answer
#    aggAns = workTimeAndApprovalRate.groupby('HITId')['AnswerLabel'].agg(pd.Series.mode).to_frame()
#
#    # count number of pros and cons and compute inter-rater rate
#    zdf = workTimeAndApprovalRate.filter(['HITId', 'AnswerLabel'])
#    numCnt = zdf.groupby('HITId')['AnswerLabel'].value_counts().to_frame()
#    counts = zdf.groupby('HITId')['AnswerLabel'].value_counts('counts').to_frame()
#    irate = counts.groupby('HITId')['AnswerLabel'].max()
#
#    # This method deals with one entity and one relation input and search in the cleaned crowd data if
#    def searchInCrowd(self, entity, relation, graph, WDT, WD, cleanedCrowdDataSet, aggAns, numCnt, irate):
#        relid = getRelWDTid(graph, WDT, relation)
#        entURI = getEntURI(graph, entity)
#        entid = getEntIdByURI(WD, entURI[0])
#
#        rate = 0
#        lbl = 0
#        lblRev = 0
#        cnt1 = 0
#        cnt2 = 0
#        # check if entity and relation exist in crowd data
#        if len(relid) != 0 and len(entid) != 0:
#            wdtRelid = 'wdt:{}'.format(relid[0])
#            wdtEntid = 'wd:{}'.format(entid)
#            res1 = cleanedCrowdDataSet[(cleanedCrowdDataSet['Input2ID'] == wdtRelid) & (cleanedCrowdDataSet['Input1ID'] == wdtEntid)]
#            res2 = cleanedCrowdDataSet[(cleanedCrowdDataSet['Input2ID'] == wdtRelid) & (cleanedCrowdDataSet['Input3ID'] == wdtEntid)]
#            print("res1: ", res1)
#            print("res2: ", res2)
#            if not res1.empty or not res2.empty:
#                print("IS IN CROWD")
#                isInCrowd = True
#                hitid = list(set.union(set(res1['HITId']), set(res2['HITId'])))[0]
#                ans = aggAns.iloc[hitid - 1]
#                print("ans: ", ans)
#                lbl = ans['AnswerLabel']
#                print("THE lbl: ", lbl)
#                #lbl = list(lbl)
#                if lbl == 'CORRECT':
#                    print('1')
#                    lblRev = 'INCORRECT'
#                elif lbl == 'INCORRECT':
#                    print('2')
#                    lblRev = 'CORRECT'
#                elif lbl == ['CORRECT', 'INCORRECT']:
#                    print('3')
#                    lbl = 'CORRECT'
#                    lblRev = 'INCORRECT'
#                print("were heere", lbl, lblRev)
#                name = (hitid, lbl)
#                nameRev = (hitid, lblRev)
#                print("name: ", name)
#                print("name namerevv",name, nameRev)
#
#                for idx in range(len(numCnt)):
#                    if numCnt.iloc[idx].name == name:
#                        cnt1 = numCnt.iloc[idx]['AnswerLabel']
#                    if numCnt.iloc[idx].name == nameRev:
#                        cnt2 = numCnt.iloc[idx]['AnswerLabel']
#                rate = irate.iloc[hitid - 1]
#
#            else:
#                isInCrowd = False
#        else:
#            isInCrowd = False
#
#        return isInCrowd, rate, lbl, cnt1, lblRev, cnt2, corrAns


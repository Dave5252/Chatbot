from EntityAndRealtion import *
import pandas as pd


class Crowd:
    # load crowdsource data
    crowdSource = pd.read_csv(r'C:\Users\David\Desktop\Chatbot\Data\crowd_data.tsv', sep='\t')
    # filter out malicious workers by their WorkTimeInSeconds
    workTimeAndApprovalRate = crowdSource.filter(['HITId', 'WorkTimeInSeconds', 'WorkerId', 'LifetimeApprovalRate'], axis=1)
    workTimeAndApprovalRate['LifetimeApprovalRate'] = workTimeAndApprovalRate['LifetimeApprovalRate'].str.replace('%', '').astype(float)
    malHits = workTimeAndApprovalRate.loc[workTimeAndApprovalRate.groupby('HITId')['WorkTimeInSeconds'].idxmin()]
    # Filter out malicious workers by their LifetimeApprovalRate
    malAllTimeRat = workTimeAndApprovalRate.loc[workTimeAndApprovalRate.groupby('HITId')['LifetimeApprovalRate'].idxmin()]
    maliWorkers = malHits['WorkerId'].unique()
    cleanData = crowdSource
    for malWk in maliWorkers:
        # drop all malicious workers from the crowd data
        cleanedData = cleanData.drop(cleanData[(cleanData['WorkerId'] == malWk)].index)
    # drop all HITs that have low rating
    maliWorkers = malAllTimeRat['WorkerId'].unique()
    cleanData2 = cleanedData
    for malWk in maliWorkers:
        # drop all malicious workers from the crowd data
        cleanedDataFinal = cleanData2.drop(cleanData2[(cleanData2['WorkerId'] == malWk)].index)
    # aggregate worker answers and get the answer
    aggAns = cleanedDataFinal.groupby('HITId')['AnswerLabel'].agg(pd.Series.mode).to_frame()

    # count number of pros and cons and compute inter-rater rate
    zdf = cleanedDataFinal.filter(['HITId', 'AnswerLabel'])
    numCnt = zdf.groupby('HITId')['AnswerLabel'].value_counts().to_frame()
    counts = zdf.groupby('HITId')['AnswerLabel'].value_counts('counts').to_frame()
    irate = counts.groupby('HITId')['AnswerLabel'].max()

    # This method deals with one entity and one relation input and search in the cleaned crowd data if exist
    def checkCrowdER(self, entity, relation, graph, WDT, WD, cleanCrowd, aggAns, numCnt, irate):
        relid = getRelWDTid(graph, WDT, relation)
        entURI = getEntURI(graph, entity)
        entid = getEntIdByURI(WD, entURI[0])

        rate = 0
        lbl = 0
        lblRev = 0
        cnt1 = 0
        cnt2 = 0
        # check if entity and relation exist in crowd data
        if len(relid) != 0 and len(entid) != 0:
            wdtRelid = 'wdt:{}'.format(relid[0])
            wdtEntid = 'wd:{}'.format(entid)
            res1 = cleanCrowd[(cleanCrowd['Input2ID'] == wdtRelid) & (cleanCrowd['Input1ID'] == wdtEntid)]
            res2 = cleanCrowd[(cleanCrowd['Input2ID'] == wdtRelid) & (cleanCrowd['Input3ID'] == wdtEntid)]

            print(res1, res2)
            if not res1.empty or not res2.empty:
                hitid = set.union(set(res1['HITId']), set(res2['HITId']))
                incrowd = True
                hitid = list(hitid)[0]
                ans = aggAns.iloc[hitid - 1]
                lbl = ans['AnswerLabel']
                lbl = list(lbl)
                print(lbl)
                if lbl == 'CORRECT':
                    print('1')
                    lblRev = 'INCORRECT'
                elif lbl == 'INCORRECT':
                    print('2')
                    lblRev = 'CORRECT'
                elif lbl == ['CORRECT', 'INCORRECT']:
                    print('3')
                    lbl = 'CORRECT'
                    lblRev = 'INCORRECT'
                print(lbl, lblRev)
                name = (hitid, lbl)
                nameRev = (hitid, lblRev)

                print(name, nameRev)
                for idx in range(105):
                    if numCnt.iloc[idx].name == name:
                        cnt1 = numCnt.iloc[idx]['AnswerLabel']
                    if numCnt.iloc[idx].name == nameRev:
                        cnt2 = numCnt.iloc[idx]['AnswerLabel']
                rate = irate.iloc[hitid - 1]

            else:
                incrowd = False
        else:
            incrowd = False

        return incrowd, rate, lbl, cnt1, lblRev, cnt2

    # this method deals with two entities as input
    # TODO: delete this method
    def checkCrowdEE(self, entity1, entity2, graph, WDT, WD, cleanCrowd, aggAns, numCnt, irate):
        entURI1 = getEntURI(graph, entity1)
        entid1 = getEntIdByURI(WD, entURI1[0])

        entURI2 = getEntURI(graph, entity2)
        entid2 = getEntIdByURI(WD, entURI2[0])

        rate = 0
        lbl = 0
        lblRev = 0
        cnt1 = 0
        cnt2 = 0
        if len(entid1) != 0 and len(entid2) != 0:
            wdtEntid1 = 'wd:{}'.format(entid1)
            wdtEntid2 = 'wd:{}'.format(entid2)

            res1 = cleanCrowd[(cleanCrowd['Input3ID'] == wdtEntid2) & (cleanCrowd['Input1ID'] == wdtEntid1)]
            res2 = cleanCrowd[(cleanCrowd['Input3ID'] == wdtEntid1) & (cleanCrowd['Input1ID'] == wdtEntid2)]

            print(res1, res2)
            if not res1.empty or not res2.empty:
                hitid = set.union(set(res1['HITId']), set(res2['HITId']))

                incrowd = True
                hitid = list(hitid)[0]

                ans = aggAns.iloc[hitid - 1]
                lbl = ans['AnswerLabel']
                lbl = list(lbl)
                print(lbl)
                if lbl == 'CORRECT':
                    print('1')
                    lblRev = 'INCORRECT'
                elif lbl == 'INCORRECT':
                    print('2')
                    lblRev = 'CORRECT'
                elif lbl == ['CORRECT', 'INCORRECT']:
                    print('3')
                    lbl = 'CORRECT'
                    lblRev = 'INCORRECT'
                print(lbl, lblRev)
                name = (hitid, lbl)
                nameRev = (hitid, lblRev)

                print(name, nameRev)
                for idx in range(105):
                    if numCnt.iloc[idx].name == name:
                        cnt1 = numCnt.iloc[idx]['AnswerLabel']
                    if numCnt.iloc[idx].name == nameRev:
                        cnt2 = numCnt.iloc[idx]['AnswerLabel']
                rate = irate.iloc[hitid - 1]


            else:
                incrowd = False
        else:
            incrowd = False
        return incrowd, rate, lbl, cnt1, lblRev, cnt2

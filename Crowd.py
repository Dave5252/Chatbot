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
    # count number of pros and cons and compute inter-rater rate
    batches = workTimeAndApprovalRate['HITTypeId'].unique()
    # calc of inter-rater agreement
    kappa_values = {}
    for batch in batches:
        df = workTimeAndApprovalRate[workTimeAndApprovalRate.HITTypeId == batch]
        indices = df.groupby(['HITId']).groups
        total_correct = 0
        total_incorrect = 0
        p_i_total = 0
        questions = 0
        for (idx), _ in indices.items():
            n_corr = df[(df.HITId == idx) & (df.AnswerLabel == 'CORRECT')].shape[0]
            n_incorr = df[(df.HITId == idx) & (df.AnswerLabel == 'INCORRECT')].shape[0]
            mis_p = ''
            coo_label = ''

            for _, row in df[df.HITId == idx].iterrows():
                row.fillna('', inplace=True)
                if row.FixPosition != '':
                    mis_p = row.FixPosition
                if row.FixValue != '':
                    coo_label = row.FixValue
            n_answer = n_corr + n_incorr
            p_i = 1 / (n_answer * (n_answer - 1)) * (n_corr * (n_corr - 1) + n_incorr * (n_incorr - 1))

            total_correct += n_corr
            total_incorrect += n_incorr
            p_i_total += p_i
            questions += 1

        total_answer = total_correct + total_incorrect
        p_correct = total_correct / total_answer
        p_incorrect = total_incorrect / total_answer
        p_i_mean = p_i_total / questions
        p_e = p_correct ** 2 + p_incorrect ** 2
        kappa_values[batch] = (p_i_mean - p_e) / (1 - p_e)

    def searchInCrowd(self, entity, relation, graph, WDT, WD, cleanedCrowdDataSet, kappa_values):
        """
        Search in crowdsource data for the given entity and relation
        :param entity: entity from the question
        :param relation: relation from the question
        :param graph: graph
        :param WDT: wikidata prefix
        :param WD: wikidata prefix
        :param cleanedCrowdDataSet: cleaned crowdsource data with  approvalrate >= 50 and worktime >= 10.
        :param kappa_values: inter-rater agreement
        :return: Return the number of pros and cons, the correct answer, and the inter-rater rate, if the entity and
        relation are in the crowdsource data.
        """
        isInCrowd = False
        relid = getRelWDTid(graph, WDT, relation)
        entURI = getEntURI(graph, entity)
        lbl = 0
        lblRev = 0
        incorr = 0
        corr = 0
        corrans = {}
        inter = 0
        frominput3 = False
        # check if entity and relation exist in crowd data
        for ent in entURI:
            entid = getEntIdByURI(WD, ent)
            print("crowd ent & rel", entid, relid)
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
                    HITTypeId = res1['HITTypeId'].values[0]
                    inter = kappa_values[HITTypeId]
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


            # take the answer with the highest number of votes
            nogos = ["I don't understand", "Object", "Subject", "Predicate", "Object", "Predicate", "NaN"]
            corrans = {k: v for k, v in corrans.items() if k not in nogos}
            if frominput3 and incorr > corr:
                corrans = {}
            if len(corrans) > 0:
                corrans = max(corrans, key=corrans.get)
                print("corrans", corrans)
                if corrans.startswith("wd") or corrans.startswith("Q"):
                    if corrans.startswith("wd"):
                        corrans = corrans.replace("wd:", "")
                    entlist = set(graph.query("""
                    prefix wdt: <http://www.wikidata.org/prop/direct/>
                    prefix wd: <http://www.wikidata.org/entity/>
                    SELECT DISTINCT * WHERE {{
                    wd:{} rdfs:label ?label . 
                    FILTER (langMatches( lang(?label), "en" ) )  
                    }}""".format(corrans)))
                    corrans = [str(ent.label) for ent in entlist]
                    if len(corrans) >0:
                        corrans = corrans[0]
        if type(corrans) == str:
            if corrans.startswith("wdt") or corrans.startswith("P"):
                corrans = corrans.replace("wdt:", "")
                entlist = set(graph.query("""
                prefix wdt: <http://www.wikidata.org/prop/direct/>
                prefix wd: <http://www.wikidata.org/entity/>
                SELECT DISTINCT * WHERE {{
                wd:{} rdfs:label ?label . 
                FILTER (langMatches( lang(?label), "en" ) )  
                }}""".format(corrans)))
                corrans = [str(ent.label) for ent in entlist]
        if len(corrans) > 0 and type(corrans) == list:
            corrans = corrans[0]
        return isInCrowd, inter.__round__(4), lbl, corr, lblRev, incorr, corrans

# query: entity URI
queryLabel = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?label
    WHERE {{
        wd:{} rdfs:label ?label.
        }}'''

# query one entity and one relation, find the other entity qid
queryOneRelOneEnt = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?objU
    WHERE {{
        ?sujU rdfs:label "{}"@en.
        ?sujU wdt:{} ?objU.
        }}'''



# query: given human name search for imdbid
humanImdbIdTemp = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?imdbid
    WHERE {{
        ?human rdfs:label "{}"@en .       
        ?human rdfs:label ?humanLbl .
        ?human wdt:P345 ?imdbid .
        }}'''
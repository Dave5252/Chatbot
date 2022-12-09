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

# query: for given two entities and find if relation exist
query_template2 = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?relL
    WHERE {{
        ?sujU rdfs:label "{}"@en.
        ?objU rdfs:label "{}"@en.
        ?objU wdt:P31 wd:Q11424 .
        ?objU ?rel ?sujU .
        ?rel rdfs:label ?relL
        }}'''
# query: switch direction
query_template3 = '''
    prefix wdt: <http://www.wikidata.org/prop/direct/>
    prefix wd: <http://www.wikidata.org/entity/>

    SELECT ?relL
    WHERE {{
        ?sujU rdfs:label "{}"@en.
        ?objU rdfs:label "{}"@en.
        ?objU wdt:P31 wd:Q11424 .
        ?sujU ?rel ?objU .
        ?rel rdfs:label ?relL
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
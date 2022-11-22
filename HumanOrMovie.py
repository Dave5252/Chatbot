from Queries import isHumanTemp, isFilmTemp


def humanOrFilm(graph, entity):
    global human, film
    is_human_query = isHumanTemp.format(entity)
    is_human = set(graph.query(is_human_query))
    is_film_query = isFilmTemp.format(entity)
    is_film = set(graph.query(is_film_query))
    if len(is_human) == 0:
        human = False
    else:
        for row in is_human:
            if 'P31' in str(row.rel):
                human = True
                print("ishuman")
    if len(is_film) == 0:
        film = False
    else:
        for row in is_film:
            if 'P31' in str(row.rel):
                film = True
                print("isfilm")
    return human, film

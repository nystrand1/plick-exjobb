import logging
import redis
import json
cache = redis.Redis(host='redis', port=6379)


def get_query_candidates(db, seperate_brand_categories = False):
    if(seperate_brand_categories):
        res = db.session.execute("""
        SELECT query, count(record.query) as amount, cat.name as category, brand.name as brand
        FROM plick.search_record as record
        LEFT JOIN plick.categories as cat on cat.id = ANY(record.category_ids)
        LEFT JOIN plick.brands as brand on brand.id = ANY(record.brand_ids)
        WHERE LENGTH(query) > 1
        AND
        record.created_at > '2021-03-15'::date - interval '7 day'
        GROUP BY query, cat.name, brand.name
        HAVING count(query) > 100
        ORDER BY amount DESC
        """)
    else:    
        res = db.session.execute("""
        SELECT query, count(query) as amount
        FROM plick.search_record
        WHERE LENGTH(query) > 1
        AND
        created_at > '2021-03-15'::date - interval '7 day'
        GROUP BY query
        HAVING count(query) > 300
        ORDER BY amount DESC
        """)

    res_arr = []

    for r in res:
        res_arr.append(r)
    
    return res_arr


def use_strict(query):
    splitted = query.split()
    return len(splitted) > 1 and len(splitted[0]) > 2 and len(splitted[1]) > 2


def get_similar_words(db, query, similarity_threshold = 0.59):
    CACHE_KEY = "_SIMQUERY:{}_SIMTHRESHOLD:{}".format(query, similarity_threshold)
    
    if (cache.get(CACHE_KEY)):
        logging.debug("GETTING SIMILAR WORDS FROM CACHE")
        return json.loads(cache.get(CACHE_KEY))

    # method = "word_similarity"
    # if(use_strict(query)):
    #     similarity_threshold = 0.6
    #     method = "strict_word_similarity"

    # logging.debug("USING METHOD: {}".format(method))
    res = db.session.execute("""
    SET work_mem='12MB';
    SET pg_trgm.similarity_threshold = :threshold;
    SET pg_trgm.word_similarity_threshold = :threshold;
    SET pg_trgm.strict_word_similarity_threshold = :threshold;
    SELECT query, similarity(query, :query) as sim,
    word_similarity(query, :query) as word_sim,
    strict_word_similarity(query, :query) as strict_word_sim,
    count(query) as amount
    FROM plick.search_record
    WHERE 
    :query % query
    AND
    :query %> query
    AND
    :query %>> query
    GROUP BY query
    HAVING count(query) > 100
    ORDER BY sim DESC
    """, {
        'query': query,
        'threshold': similarity_threshold,
    })

    res_arr = []

    for r in res:
        res_arr.append(r['query'])

    cache.set(CACHE_KEY, json.dumps(res_arr), 300)
    return res_arr


def get_trending_words(db, limit=5, k_threshold=0):
    res = db.session.execute("""
    SELECT query, similar_queries, model_short, model_long
    FROM plick.term_trends
    WHERE model_short[1] + :threshold > model_long[1]
    AND model_short[1] > 1
    ORDER BY model_short[1] DESC
    LIMIT :limit
    """, {
        'limit': limit,
        'threshold': k_threshold
    })

    res_arr = []

    for r in res:
        tmp = dict()
        tmp['query'] = r['query']
        tmp['similar_queries'] = r['similar_queries']
        res_arr.append(tmp)
    return res_arr  
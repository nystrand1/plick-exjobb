import logging


def get_query_candidates(db, seperate_brand_categories = False):
    if(seperate_brand_categories):
        res = db.session.execute("""
        SELECT query, count(record.query) as amount, cat.name as category, brand.name as brand
        FROM search_records.search_record as record
        LEFT JOIN search_records.categories as cat on cat.id = ANY(record.category_ids)
        LEFT JOIN search_records.brands as brand on brand.id = ANY(record.brand_ids)
        WHERE LENGTH(query) > 1
        AND
        record.created_at > '2021-02-18'::date - interval '7 day'
        GROUP BY query, cat.name, brand.name
        HAVING count(query) > 100
        ORDER BY amount DESC
        """)
    else:    
        res = db.session.execute("""
        SELECT query, count(query) as amount
        FROM search_records.search_record
        WHERE LENGTH(query) > 1
        AND
        created_at > '2021-02-18'::date - interval '7 day'
        GROUP BY query
        HAVING count(query) > 1000
        ORDER BY amount DESC
        """)

    res_arr = []

    for r in res:
        r = dict(r.items())
        res_arr.append(r)
    
    return res_arr
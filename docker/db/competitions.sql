-- The competitions list stored by `make load` or `make fetch`, filtered on one year: it gives the ids for `fetch --competition`.
SELECT e->>'id_competition' AS id, e->>'date_from' AS starts, e->>'rank_name' AS rank, e->>'name' AS name
FROM ingestion.raw_response, jsonb_array_elements(payload) AS e
WHERE endpoint = 'competition.get_list' AND e->>'comp_year' = :'year' AND e->>'is_teams' = '0'
ORDER BY e->>'date_from', e->>'name';

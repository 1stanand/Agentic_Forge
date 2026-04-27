from forge.core.db import get_conn, get_cursor, release_conn

conn = get_conn()
with get_cursor(conn) as cur:
    cur.execute('SELECT COUNT(*) as cnt FROM steps WHERE screen_context IS NOT NULL')
    result = cur.fetchone()
    with_context = result['cnt']

    cur.execute('SELECT COUNT(*) as cnt FROM steps')
    result = cur.fetchone()
    total = result['cnt']

    print(f'Steps WITH screen_context: {with_context}')
    print(f'Steps total: {total}')
    print(f'Percentage populated: {(with_context/total)*100:.1f}%')

    cur.execute('SELECT DISTINCT screen_context FROM steps WHERE screen_context IS NOT NULL LIMIT 10')
    rows = cur.fetchall()
    print(f'\nSample screen_context values:')
    for row in rows:
        print(f"  {row['screen_context']}")

release_conn(conn)

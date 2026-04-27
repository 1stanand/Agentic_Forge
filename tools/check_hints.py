from forge.core.db import get_conn, get_cursor, release_conn

conn = get_conn()
with get_cursor(conn) as cur:
    cur.execute('SELECT DISTINCT stage_hint FROM doc_chunks WHERE stage_hint IS NOT NULL')
    hints = cur.fetchall()
    distinct = [h['stage_hint'] for h in hints]
    print(f'Distinct stage_hints: {distinct}')

    cur.execute('SELECT COUNT(*) as cnt FROM doc_chunks WHERE stage_hint IS NOT NULL')
    result = cur.fetchone()
    with_hint = result['cnt']
    print(f'Chunks WITH stage_hint: {with_hint}')

    cur.execute('SELECT COUNT(*) as cnt FROM doc_chunks WHERE stage_hint IS NULL')
    result = cur.fetchone()
    without_hint = result['cnt']
    print(f'Chunks WITHOUT stage_hint: {without_hint}')

    cur.execute('SELECT DISTINCT screen_hint FROM doc_chunks WHERE screen_hint IS NOT NULL')
    hints = cur.fetchall()
    distinct_screen = [h['screen_hint'] for h in hints]
    print(f'Distinct screen_hints: {distinct_screen}')

    # Show first few chunks
    cur.execute('SELECT chunk_id, section_title, stage_hint, screen_hint FROM doc_chunks LIMIT 5')
    rows = cur.fetchall()
    print('\nFirst 5 chunks:')
    for row in rows:
        print(f"  {row['chunk_id']}: section={row['section_title']}, stage={row['stage_hint']}, screen={row['screen_hint']}")

release_conn(conn)

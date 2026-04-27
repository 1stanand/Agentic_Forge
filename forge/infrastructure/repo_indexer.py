import argparse, glob, json, logging, os, sys, time
from forge.core.config import get_settings
from forge.core.db import get_conn, release_conn, get_cursor
from forge.infrastructure.feature_parser import parse_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)-7s  %(message)s')
logger = logging.getLogger(__name__)

def db_fetch_all_mtimes(conn):
    with get_cursor(conn) as cur:
        cur.execute('SELECT file_path, mtime FROM features')
        return {row['file_path']: row['mtime'] for row in cur.fetchall()}

def db_delete_feature(conn, file_path: str):
    with get_cursor(conn) as cur:
        cur.execute('DELETE FROM features WHERE file_path = %s', (file_path,))
    conn.commit()

def db_insert_feature(conn, parsed: dict, mtime: float):
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                'INSERT INTO features (file_path, file_name, folder_path, file_tags, file_dicts, flow_type, has_conflict, parse_error, mtime) VALUES (%s,%s,%s, %s,%s::jsonb, %s,%s,%s,%s) RETURNING id',
                (parsed['file_path'], parsed['file_name'], parsed.get('folder_path', ''),
                 parsed['file_tags'], json.dumps(parsed['file_dicts']),
                 parsed['flow_type'], parsed['has_conflict'], parsed['parse_error'], mtime))
            feature_id = cur.fetchone()['id']

            for sc in parsed['scenarios']:
                cur.execute(
                    'INSERT INTO scenarios (feature_id, title, scenario_type, scenario_tags, scenario_dicts, position) VALUES (%s,%s,%s, %s,%s::jsonb,%s) RETURNING id',
                    (feature_id, sc['title'], sc['scenario_type'],
                     sc['scenario_annotations'], json.dumps(sc['scenario_dicts']), sc['scenario_index']))
                scenario_id = cur.fetchone()['id']

                if sc['steps']:
                    step_rows = [(scenario_id, 1, s['keyword'], s['step_text'], s['step_position'], s.get('screen_context')) for s in sc['steps']]
                    cur.executemany('INSERT INTO steps (scenario_id, feature_id, step_keyword, step_text, step_position, screen_context) VALUES (%s,%s,%s,%s,%s,%s)', step_rows)

                for eb in sc['example_blocks']:
                    cur.execute(
                        'INSERT INTO example_blocks (scenario_id, block_position, headers, rows, block_dicts) VALUES (%s,%s,%s,%s,%s::jsonb)',
                        (scenario_id, eb['block_index'], eb['headers'], json.dumps(eb['rows']), json.dumps(eb['block_dicts'])))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def db_refresh_unique_steps(conn):
    with get_cursor(conn, dict_cursor=False) as cur:
        cur.execute('REFRESH MATERIALIZED VIEW unique_steps')
    conn.commit()

def db_total_counts(conn):
    with get_cursor(conn) as cur:
        cur.execute('SELECT COUNT(*) AS n FROM features')
        n_files = cur.fetchone()['n']
        cur.execute('SELECT COUNT(*) AS n FROM scenarios')
        n_scen = cur.fetchone()['n']
        cur.execute('SELECT COUNT(*) AS n FROM steps')
        n_steps = cur.fetchone()['n']
        cur.execute('SELECT COUNT(*) AS n FROM unique_steps')
        n_unique = cur.fetchone()['n']
    return {'files': n_files, 'scenarios': n_scen, 'steps': n_steps, 'unique_steps': n_unique}

def find_feature_files(repo_path: str):
    pattern = os.path.join(repo_path, '**', '*.feature')
    all_files = [os.path.normpath(p) for p in glob.glob(pattern, recursive=True)]
    excluded = {'PickApplication.feature', 'OpenApplication.feature'}
    return [f for f in all_files if os.path.basename(f) not in excluded]

def run_ingest(repo_path: str, full_rebuild: bool = False):
    repo_path = os.path.normpath(str(repo_path))
    if not os.path.isdir(repo_path):
        logger.error('repo-path does not exist: %s', repo_path)
        sys.exit(1)

    conn = get_conn()

    if full_rebuild:
        logger.info('Full rebuild - running setup_db...')
        from forge.scripts.setup_db import setup_db
        setup_db()
        logger.info('Schema recreated.')

    logger.info('Scanning %s...', repo_path)
    disk_files = set(find_feature_files(repo_path))
    logger.info('Found %d .feature files.', len(disk_files))

    existing = db_fetch_all_mtimes(conn)
    new_files, changed_files, deleted_files = [], [], []

    for fpath in disk_files:
        mtime = os.path.getmtime(fpath)
        if fpath not in existing:
            new_files.append(fpath)
        elif abs(existing[fpath] - mtime) > 0.001:
            changed_files.append(fpath)

    for fpath in existing:
        if fpath not in disk_files:
            deleted_files.append(fpath)

    logger.info('New: %d | Changed: %d | Unchanged: %d | Deleted: %d', len(new_files), len(changed_files), len(disk_files) - len(new_files) - len(changed_files), len(deleted_files))

    for fpath in deleted_files:
        db_delete_feature(conn, fpath)
    for fpath in changed_files:
        db_delete_feature(conn, fpath)

    to_parse = new_files + changed_files
    if not to_parse:
        logger.info('Nothing to parse.')
    else:
        logger.info('Parsing %d file(s)...', len(to_parse))
        n_ok, n_error, n_scenarios, n_steps = 0, 0, 0, 0
        t0 = time.perf_counter()
        for i, fpath in enumerate(to_parse, 1):
            mtime = os.path.getmtime(fpath)
            parsed = parse_file(fpath)
            if parsed['parse_error']:
                logger.warning('[%d/%d] PARSE ERROR %s', i, len(to_parse), os.path.basename(fpath))
                n_error += 1
                continue
            try:
                db_insert_feature(conn, parsed, mtime)
                n_ok += 1
                n_scenarios += len(parsed['scenarios'])
                n_steps += sum(len(sc['steps']) for sc in parsed['scenarios'])
            except Exception as exc:
                logger.error('[%d/%d] DB INSERT FAILED %s: %s', i, len(to_parse), os.path.basename(fpath), exc)
                n_error += 1
            if i % 100 == 0:
                logger.info('Progress: %d/%d', i, len(to_parse))
        logger.info('Parsed %d in %.1fs | OK: %d Errors: %d Scenarios: +%d Steps: +%d', len(to_parse), time.perf_counter() - t0, n_ok, n_error, n_scenarios, n_steps)

    logger.info('Refreshing unique_steps...')
    db_refresh_unique_steps(conn)

    totals = db_total_counts(conn)
    logger.info('Done. Files: %d Scenarios: %d Steps: %d Unique: %d', totals['files'], totals['scenarios'], totals['steps'], totals['unique_steps'])
    release_conn(conn)

def main():
    parser = argparse.ArgumentParser(description='Forge - ingest ATDD features')
    parser.add_argument('--full-rebuild', action='store_true')
    args = parser.parse_args()
    settings = get_settings()
    if not settings.features_repo_path:
        logger.error('FEATURES_REPO_PATH not set in .env')
        sys.exit(1)
    run_ingest(str(settings.features_repo_path), full_rebuild=args.full_rebuild)

if __name__ == '__main__':
    main()

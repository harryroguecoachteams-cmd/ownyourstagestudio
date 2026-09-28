"""Deploy the OYSS signed-agreements / receipts relay to the RCT cPanel.

    python _relay/deploy.py            # code, test key, token if present, cron
    python _relay/deploy.py --check    # only the live status + diagnostics

Private files go OUTSIDE the web root, in /home/rogucmxm/oyss_private:
lib.php, minipdf.php, receipts_job.php, receipts.php, test_key.txt and, once
Harsh has made it, ghl_pit.txt (Annette's GHL Private Integration token).
The one public file is public_html/relay/oyss-docs.php.

Secrets live only in E:/_shared/secrets (never in this public repo):
  oyss_docs_test.txt  the test key for the diagnostics and dry runs (made here)
  oyss_ghl_pit.txt    the GHL token, one line (Harsh creates it; see RESUME.md)
"""
import datetime, json, pathlib, secrets, sys, urllib.parse, urllib.request

sys.path.insert(0, r'E:/_shared/cpanel')
import deploy_cpanel as D  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
SECRETS = pathlib.Path(r'E:/_shared/secrets')
HOME = '/home/rogucmxm'
PRIV = HOME + '/oyss_private'
PUB = HOME + '/public_html/relay'
URL = 'https://roguecoachteams.com/relay/oyss-docs.php'


def save(dirpath, name, content):
    res = D.call('/execute/Fileman/save_file_content', None,
                 data=urllib.parse.urlencode({'dir': dirpath, 'file': name, 'content': content}).encode(),
                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if not res.get('status'):
        sys.exit(f'save {dirpath}/{name} failed: {res.get("errors")}')
    print('saved', f'{dirpath}/{name}', len(content))


def mkdir(parent, name):
    try:
        D.api2('Fileman', 'mkdir', {'path': parent, 'name': name, 'permissions': '0700'})
        print('mkdir', f'{parent}/{name}')
    except SystemExit as e:
        if 'exist' not in str(e).lower():
            print('mkdir note:', e)


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'oyss-deploy'}), timeout=60) as r:
        return json.loads(r.read())


def main():
    key_file = SECRETS / 'oyss_docs_test.txt'
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(24))
    key = key_file.read_text().strip()

    if '--check' not in sys.argv:
        mkdir(HOME, 'oyss_private')
        mkdir(PRIV, 'state')
        mkdir(HOME + '/public_html', 'relay')
        start = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
        existing = ''
        try:
            existing = get(URL + '?t=' + key).get('receipts_from', '')
        except Exception:
            pass
        for name in ('lib.php', 'minipdf.php', 'receipts.php'):
            save(PRIV, name, (HERE / name).read_text(encoding='utf-8'))
        job = (HERE / 'receipts_job.php').read_text(encoding='utf-8')
        save(PRIV, 'receipts_job.php', job.replace('%%RECEIPTS_FROM%%', existing or start))
        save(PRIV, 'test_key.txt', key)
        pit = SECRETS / 'oyss_ghl_pit.txt'
        if pit.exists() and pit.read_text().strip():
            save(PRIV, 'ghl_pit.txt', pit.read_text().strip())
        else:
            print('no GHL token yet (E:/_shared/secrets/oyss_ghl_pit.txt): the relay answers not_configured')
        save(PUB, 'oyss-docs.php', (HERE / 'oyss-docs.php').read_text(encoding='utf-8'))
        for f in ('ghl_pit.txt', 'test_key.txt'):
            try:
                D.api2('Fileman', 'fileop', {'op': 'chmod', 'sourcefiles': f'{PRIV}/{f}', 'metadata': '0600'})
            except SystemExit:
                pass

    print('public :', get(URL))
    diag = get(URL + '?t=' + key)
    print('diag   :', json.dumps({k: diag.get(k) for k in ('php', 'binary', 'cli', 'curl', 'iconv', 'zlib', 'configured', 'state_writable')}))
    for line in diag.get('log', [])[-8:]:
        print('log    :', line)


if __name__ == '__main__':
    main()

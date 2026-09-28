<?php
/*
 * https://roguecoachteams.com/relay/oyss-docs.php
 *
 * The agreement pages on ownyourstagestudio.com post the signed PDF here
 * the moment it is made (the same PDF the signer downloads). It is filed in
 * Annette's GHL and emailed to the signer from events@ with Annette in Bcc.
 * See lib.php for the whole picture.
 *
 * POST (from the live site only): JSON sent as text/plain, so no preflight.
 * GET: a status line. With the test key: diagnostics, a sample receipt PDF,
 * or a run of the receipts job (dry by default).
 */

$lib = is_file(__DIR__ . '/../../oyss_private/lib.php') ? __DIR__ . '/../../oyss_private/lib.php' : __DIR__ . '/lib.php';
require $lib;
require_once PRIV . '/receipts_job.php';

$ORIGINS = array('https://ownyourstagestudio.com', 'https://www.ownyourstagestudio.com');

function out($code, $arr)
{
    http_response_code($code);
    header('Content-Type: application/json');
    header('Cache-Control: no-store');
    echo json_encode($arr);
    exit;
}

function test_key_ok()
{
    $f = PRIV . '/test_key.txt';
    $given = isset($_GET['t']) ? (string) $_GET['t'] : (isset($_SERVER['HTTP_X_OYSS_TEST']) ? (string) $_SERVER['HTTP_X_OYSS_TEST'] : '');
    if ($given === '' || !is_file($f)) return false;
    return hash_equals(trim((string) file_get_contents($f)), $given);
}

/* a sliding count in a state file: at most $max in $window seconds */
function allow($key, $max, $window)
{
    $name = 'rl_' . substr(sha1($key), 0, 20) . '.json';
    $now = time();
    $hits = array_values(array_filter(state_get($name, array()), function ($t) use ($now, $window) { return $t > $now - $window; }));
    if (count($hits) >= $max) return false;
    $hits[] = $now;
    state_put($name, $hits);
    return true;
}

$origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';
if (in_array($origin, $ORIGINS, true)) {
    header('Access-Control-Allow-Origin: ' . $origin);
    header('Vary: Origin');
}
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header('Access-Control-Allow-Methods: POST');
    header('Access-Control-Allow-Headers: Content-Type');
    http_response_code(204);
    exit;
}
$test = test_key_ok();

/* ------------------------------------------------------------------ GET */
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (!$test) out(200, array('ok' => true, 'service' => 'oyss-docs', 'configured' => configured()));

    $what = isset($_GET['do']) ? $_GET['do'] : 'diag';
    if ($what === 'sample') {
        $tx = array('_id' => '6aba0000c0ffee0000abc123', 'createdAt' => gmdate('c'), 'amount' => 47, 'currency' => 'USD',
                    'entitySourceName' => 'Panelist Commitment & Administrative Fee', 'status' => 'succeeded',
                    'chargeSnapshot' => array('payment_method_details' => array('card' => array('brand' => 'visa', 'last4' => '4242'))));
        $c = array('firstName' => 'Sample', 'lastName' => 'Panelist', 'email' => 'sample@example.com');
        header('Content-Type: application/pdf');
        header('Content-Disposition: inline; filename="sample-receipt.pdf"');
        echo receipt_pdf(receipt_facts($tx, $c));
        exit;
    }
    if ($what === 'receipts') {
        out(200, run_receipts(!isset($_GET['live'])));
    }
    $bins = array();
    foreach (array('/usr/local/bin/php', '/usr/bin/php', '/opt/cpanel/ea-php81/root/usr/bin/php',
                   '/opt/cpanel/ea-php82/root/usr/bin/php', '/opt/cpanel/ea-php83/root/usr/bin/php',
                   '/opt/cpanel/ea-php74/root/usr/bin/php', '/opt/cpanel/ea-php80/root/usr/bin/php') as $b) {
        if (@is_file($b)) $bins[] = $b;
    }
    $log = is_file(state_path('log.txt')) ? array_slice(file(state_path('log.txt'), FILE_IGNORE_NEW_LINES), -25) : array();
    out(200, array(
        'ok' => true, 'php' => PHP_VERSION, 'binary' => PHP_BINARY, 'cli' => $bins,
        'curl' => function_exists('curl_init'), 'iconv' => function_exists('iconv'), 'zlib' => function_exists('gzcompress'),
        'configured' => configured(), 'state_writable' => is_writable(dirname(state_path('x'))),
        'receipts_from' => strpos(RECEIPTS_FROM, '%%') === 0 ? '' : RECEIPTS_FROM,
        'receipts' => state_get('receipts.json', array()), 'log' => $log,
    ));
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, array('ok' => false, 'error' => 'method'));
if (!$test && !in_array($origin, $ORIGINS, true)) out(403, array('ok' => false, 'error' => 'origin'));

/* ------------------------------------------------------------------ POST */
$raw = file_get_contents('php://input', false, null, 0, 7000001);
if (strlen($raw) > 7000000) out(413, array('ok' => false, 'error' => 'size'));
$d = json_decode($raw, true);
if (!is_array($d)) out(400, array('ok' => false, 'error' => 'json'));

$AG = agreements();
$agreement = isset($d['agreement']) ? (string) $d['agreement'] : '';
if (!isset($AG[$agreement])) out(400, array('ok' => false, 'error' => 'agreement'));
$meta = $AG[$agreement];

$email = filter_var(isset($d['email']) ? trim($d['email']) : '', FILTER_VALIDATE_EMAIL);
if (!$email) out(400, array('ok' => false, 'error' => 'email'));
$email = strtolower($email);

$f = array();
foreach (array('first_name' => 80, 'last_name' => 120, 'legal_name' => 160, 'business_name' => 160,
               'signedAt' => 40, 'signedAtDisplay' => 60, 'signature_method' => 40,
               'agreement_version' => 40, 'signed_copy_url' => 12000, 'filename' => 200) as $k => $max) {
    $f[$k] = clean(isset($d[$k]) ? $d[$k] : '', $max);
}
$f['agreement'] = $agreement;
if ($f['legal_name'] === '') out(400, array('ok' => false, 'error' => 'legal_name'));
/* the copy link must point back at this agreement's own page */
if ($f['signed_copy_url'] !== '' && strpos($f['signed_copy_url'], $meta['page'] . '#signed=') !== 0) $f['signed_copy_url'] = '';

$pdf = base64_decode(isset($d['pdf']) ? (string) $d['pdf'] : '', true);
if ($pdf === false || substr($pdf, 0, 5) !== '%PDF-' || strlen($pdf) > 4500000) out(400, array('ok' => false, 'error' => 'pdf'));
/* It has to be the page's own signed copy for this person: the running foot
   names the agreement and the signing record carries the email address. */
if (strpos($pdf, '(' . $agreement . '  -  signed copy, ') === false ||
    (strpos($pdf, $email) === false && strpos($pdf, trim((string) $d['email'])) === false)) {
    out(400, array('ok' => false, 'error' => 'pdf content'));
}

if (!$test) {
    $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'x';
    if (!allow('ip|' . $ip, 10, 3600) || !allow('to|' . $email, 5, 86400) || !allow('all|' . gmdate('Ymd'), 100, 86400)) {
        out(429, array('ok' => false, 'error' => 'rate'));
    }
}

$dedupe = sha1($email . '|' . $agreement . '|' . $f['signedAt']);
$sent = state_get('agreements_sent.json', array());
if (isset($sent[$dedupe])) out(200, array('ok' => true, 'duplicate' => true));

$first = $f['first_name'] !== '' ? $f['first_name'] : preg_replace('/\s.*$/u', '', $f['legal_name']);
$f['first_name'] = $first;
$filename = preg_replace('/[^A-Za-z0-9 ._()-]+/', '', $f['filename']);
if ($filename === '' || substr($filename, -4) !== '.pdf') $filename = 'Signed - ' . $agreement . '.pdf';

if (!empty($d['dry']) && $test) {
    out(200, array('ok' => true, 'dry' => true, 'pdf_bytes' => strlen($pdf), 'filename' => $filename,
                   'subject' => 'Your signed ' . $agreement . ' (PDF)', 'html' => agreement_email($f, false)));
}
if (!configured()) {
    logline('agreement.not_configured', $dedupe);
    out(503, array('ok' => false, 'error' => 'not_configured'));
}

$step = 'contact';
try {
    $legalParts = preg_split('/\s+/u', $f['legal_name']);
    $contact = upsert_contact($email, $first, $f['last_name'] !== '' ? $f['last_name'] : implode(' ', array_slice($legalParts, 1)), $f['business_name']);
    $cid = $contact['id'];

    $step = 'upload';
    $url = upload_pdf($pdf, $filename, FOLDER_AGREEMENTS);

    $step = 'field';
    set_field($cid, $meta['field'], $url);

    /* paid before signing: the receipt goes along, so both documents arrive together */
    $attach = array($url);
    $lines = state_get('receipt_lines.json', array());
    $withReceipt = false;
    if (isset($lines[$cid]) && $lines[$cid] === $meta['line']) {
        $step = 'receipt lookup';
        $rurl = field_value(get_contact($cid), FIELD_RECEIPT);
        if ($rurl !== '') { $attach[] = $rurl; $withReceipt = true; }
    }

    $step = 'email';
    send_email($cid, 'Your signed ' . $agreement . ($withReceipt ? ' and your receipt' : ' (PDF)'), agreement_email($f, $withReceipt), $attach);

    $step = 'note';
    add_note($cid, 'Signed ' . $agreement . ' on ' . $f['signedAtDisplay'] . ' (' . $f['signedAt'] . '), signature ' .
        $f['signature_method'] . ($f['agreement_version'] !== '' ? ', text version ' . $f['agreement_version'] : '') . ".\n" .
        'Signed PDF (also emailed to the signer, Bcc ' . STUDIO_INBOX . '): ' . $url .
        ($f['signed_copy_url'] !== '' ? "\nSigned copy on the website: " . $f['signed_copy_url'] : ''));
    add_tags($cid, array('signed-agreement-sent'));

    $sent[$dedupe] = time();
    $sent = array_filter($sent, function ($t) { return $t > time() - 90 * 86400; });
    state_put('agreements_sent.json', $sent);
    logline('agreement.sent', $meta['line'] . ' ' . $cid . ($withReceipt ? ' +receipt' : ''));
    out(200, array('ok' => true));
} catch (Exception $e) {
    logline('agreement.error', $step . ' ' . $e->getMessage());
    out(502, array('ok' => false, 'error' => $step));
}

<?php
/*
 * The receipts: every succeeded live payment in Annette's GHL gets a
 * receipt PDF, filed in Media Storage > Payment receipts and on the contact,
 * and emailed to the payer from events@ with Annette in Bcc. The first
 * receipt for a side of the business also carries that side's signed
 * agreement when it is on the contact, so the person ends with both
 * documents in one email.
 *
 * Run by cron every five minutes (receipts.php). Only payments made after
 * RECEIPTS_FROM are touched; each one exactly once.
 */

const RECEIPTS_FROM = '%%RECEIPTS_FROM%%';   /* set at deploy, UTC */

function run_receipts($dry)
{
    if (!configured()) return array('ok' => false, 'error' => 'not_configured');
    $lock = fopen(state_path('receipts.lock'), 'c');
    if (!$lock || !flock($lock, LOCK_EX | LOCK_NB)) return array('ok' => false, 'error' => 'busy');

    $from = strpos(RECEIPTS_FROM, '%%') === 0 ? gmdate('c') : RECEIPTS_FROM;
    $st = state_get('receipts.json', array());
    $done = isset($st['done']) ? $st['done'] : array();
    $bundled = isset($st['bundled']) ? $st['bundled'] : array();
    $lines = state_get('receipt_lines.json', array());
    $report = array('ok' => true, 'dry' => $dry, 'seen' => 0, 'sent' => array(), 'skipped' => array());

    try {
        $q = http_build_query(array('altId' => LOC, 'altType' => 'location', 'locationId' => LOC,
                                    'startAt' => substr($from, 0, 10), 'limit' => 100, 'offset' => 0));
        $r = ghl('GET', '/payments/transactions?' . $q);
        $list = isset($r['data']) && is_array($r['data']) ? $r['data'] : array();
    } catch (Exception $e) {
        logline('receipts.error', 'list ' . $e->getMessage());
        return array('ok' => false, 'error' => 'list');
    }

    foreach ($list as $tx) {
        $report['seen']++;
        $id = isset($tx['_id']) ? (string) $tx['_id'] : '';
        $why = '';
        if ($id === '') $why = 'no id';
        elseif (isset($done[$id])) $why = 'done';
        elseif (!isset($tx['status']) || $tx['status'] !== 'succeeded') $why = 'status ' . (isset($tx['status']) ? $tx['status'] : '?');
        elseif (isset($tx['liveMode']) && $tx['liveMode'] === false) $why = 'test mode';
        elseif (empty($tx['contactId'])) $why = 'no contact';
        elseif (!isset($tx['createdAt']) || strtotime($tx['createdAt']) < strtotime($from)) $why = 'before start';
        if ($why !== '') { if ($why !== 'done') $report['skipped'][] = array($id, $why); continue; }

        $cid = (string) $tx['contactId'];
        $step = 'contact';
        try {
            $contact = get_contact($cid);
            if (empty($contact['email'])) { $report['skipped'][] = array($id, 'no email'); continue; }
            $facts = receipt_facts($tx, $contact);
            $pdf = receipt_pdf($facts);
            $line = payment_line($tx);
            list($agName, $ag) = agreement_for_line($line);
            $bkey = sha1($cid . '|' . $line);
            $agUrl = (!isset($bundled[$bkey]) && $ag) ? field_value($contact, $ag['field']) : '';
            $first = isset($contact['firstName']) ? trim($contact['firstName']) : '';
            $subject = $agUrl !== '' ? 'Your receipt and your signed ' . $agName : 'Your receipt from Own Your Stage Studio';

            if ($dry) {
                $report['sent'][] = array('tx' => $id, 'line' => $line, 'number' => $facts['number'], 'amount' => $facts['amount'],
                                          'subject' => $subject, 'with_agreement' => $agUrl !== '', 'pdf_bytes' => strlen($pdf));
                continue;
            }

            $step = 'upload';
            $who = preg_replace('/[^A-Za-z0-9 ._-]+/', '', $facts['name']);
            $url = upload_pdf($pdf, 'Receipt ' . $facts['number'] . ($who !== '' ? ' - ' . $who : '') . '.pdf', FOLDER_RECEIPTS);
            $step = 'field';
            set_field($cid, FIELD_RECEIPT, $url);
            $step = 'email';
            $attach = array($url);
            if ($agUrl !== '') $attach[] = $agUrl;
            send_email($cid, $subject, receipt_email($first, $facts, $agUrl !== '' ? $agName : ''), $attach);
            $step = 'note';
            add_note($cid, 'Payment receipt ' . $facts['number'] . ': ' . $facts['amount'] . ', ' . $facts['description'] .
                ', paid ' . $facts['datetime'] . ".\nReceipt PDF (also emailed to the payer, Bcc " . STUDIO_INBOX . '): ' . $url .
                ($agUrl !== '' ? "\nThe signed " . $agName . ' went with it.' : ''));
            add_tags($cid, array('receipt-sent'));

            $done[$id] = time();
            if ($agUrl !== '') $bundled[$bkey] = time();
            $lines[$cid] = $line;
            state_put('receipts.json', array('done' => $done, 'bundled' => $bundled, 'last' => gmdate('c')));
            state_put('receipt_lines.json', $lines);
            logline('receipt.sent', $line . ' ' . $cid . ' ' . $id . ($agUrl !== '' ? ' +agreement' : ''));
            $report['sent'][] = array('tx' => $id, 'number' => $facts['number']);
        } catch (Exception $e) {
            logline('receipt.error', $id . ' ' . $step . ' ' . $e->getMessage());
            $report['skipped'][] = array($id, 'error at ' . $step);
        }
    }
    if (!$dry) state_put('receipts.json', array('done' => $done, 'bundled' => $bundled, 'last' => gmdate('c')));
    flock($lock, LOCK_UN);
    return $report;
}

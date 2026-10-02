<?php
/*
 * Own Your Stage Studio: the signed agreements and the payment receipts.
 * (28 Sep 2026)
 *
 * Harsh: "make sure u add a automation to send the signed agreement and
 * payment recipt to the person email when they done with it", and the
 * signed PDFs are to be kept in Annette's own account.
 *
 * Everything lands in Annette's GoHighLevel, through her own API token
 * (a Private Integration of her sub-account):
 *   - the signed agreement PDF, and every receipt, in Media Storage
 *     (folders "Signed agreements" and "Payment receipts")
 *   - the link on the contact (custom fields) and a note on the contact
 *   - the email to the person, sent by GHL from events@ownyourstagestudio.com
 *     with the PDF attached and Annette's inbox in Bcc, logged in her
 *     Conversations like any email she sends.
 * This server only passes things through. It keeps no PDFs, and its state
 * files hold ids and hashes, never names or addresses.
 *
 * PHP 7.4 compatible (the host's version may lag).
 */

require_once __DIR__ . '/minipdf.php';

const LOC            = 'O1kebSJ9ZQAQPoaSv8lb';
const API            = 'https://services.leadconnectorhq.com';
const API_VERSION    = '2021-07-28';
const STUDIO_INBOX   = 'events@ownyourstagestudio.com';
const SITE           = 'https://ownyourstagestudio.com';
const TZ             = 'America/New_York';

const FOLDER_AGREEMENTS = '6aba4580b5e520ac173482ac';   /* Media Storage > Signed agreements */
const FOLDER_RECEIPTS   = '6aba45817ef452865a1cf081';   /* Media Storage > Payment receipts */
const FIELD_PANELIST    = '3Q7VzuoEGmOPlUMRbeE9';       /* contact.signed_panelist_agreement_pdf */
const FIELD_HOST        = 'MtwZ8bIBvgKwg5lpjExo';       /* contact.signed_host_agreement_pdf */
const FIELD_RECEIPT     = 'JM7IfUflED93E5R08NVH';       /* contact.payment_receipt_pdf */

define('PRIV', __DIR__);
define('STATE', PRIV . '/state');

function agreements()
{
    return array(
        'Featured Panelist Agreement' => array(
            'line' => 'panelist', 'field' => FIELD_PANELIST, 'page' => SITE . '/panelist-agreement',
            /* the last step, as the workflow's confirmation email had it (2 Oct 2026 this email replaced that one) */
            'pay_intro' => 'Your speaking position is confirmed once the $47 Panelist Commitment and Administrative Fee is paid.',
            'pay' => array(array('Pay the $47 fee', 'https://link.fastpaydirect.com/payment-link/6ab42a504ae1d45672839331')),
            'next' => 'We will be in touch with your preparation meeting details.',
        ),
        'Done-For-You Panel Host Services Agreement' => array(
            'line' => 'host', 'field' => FIELD_HOST, 'page' => SITE . '/host-agreement',
            'pay_intro' => 'Your event date is reserved once payment has processed and your intake is complete. Choose the option that suits you:',
            'pay' => array(array('Pay in full, $2,997', 'https://link.fastpaydirect.com/payment-link/6a8f2bcbf9c8c807930ba334'),
                           array('Two payments of $1,550', 'https://link.fastpaydirect.com/payment-link/6a919448f9c8c807930ba92c')),
            'next' => 'We will be in touch about your intake within two business days.',
        ),
    );
}

function agreement_for_line($line)
{
    foreach (agreements() as $name => $a) if ($a['line'] === $line) return array($name, $a);
    return array('', null);
}

/* ---------------------------------------------------------------- setup */

function pit()
{
    $f = PRIV . '/ghl_pit.txt';
    return is_file($f) ? trim((string) file_get_contents($f)) : '';
}

function configured()
{
    return pit() !== '';
}

function state_path($name)
{
    if (!is_dir(STATE)) @mkdir(STATE, 0700, true);
    return STATE . '/' . $name;
}

function state_get($name, $default)
{
    $f = state_path($name);
    if (!is_file($f)) return $default;
    $d = json_decode((string) file_get_contents($f), true);
    return is_array($d) ? $d : $default;
}

function state_put($name, $data)
{
    $f = state_path($name);
    file_put_contents($f . '.tmp', json_encode($data), LOCK_EX);
    rename($f . '.tmp', $f);
}

/* One line per event, ids only. Rotates at 256 KB. */
function logline($event, $detail = '')
{
    $f = state_path('log.txt');
    if (is_file($f) && filesize($f) > 262144) @rename($f, $f . '.1');
    @file_put_contents($f, gmdate('c') . "\t" . $event . "\t" . preg_replace('/\s+/', ' ', $detail) . "\n", FILE_APPEND | LOCK_EX);
}

/* ------------------------------------------------------------ GHL API */

function ghl($method, $path, $body = null, $multipart = null)
{
    $ch = curl_init(API . $path);
    $headers = array('Authorization: Bearer ' . pit(), 'Version: ' . API_VERSION, 'Accept: application/json');
    if ($multipart !== null) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, $multipart);
    } elseif ($body !== null) {
        $headers[] = 'Content-Type: application/json';
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
    }
    curl_setopt_array($ch, array(
        CURLOPT_CUSTOMREQUEST  => $method,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT        => 45,
    ));
    $raw = curl_exec($ch);
    $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $err = curl_error($ch);
    curl_close($ch);
    if ($code < 200 || $code >= 300) {
        throw new RuntimeException($method . ' ' . strtok($path, '?') . ' -> ' . $code . ' ' . substr($raw !== false ? (string) $raw : $err, 0, 300));
    }
    $data = json_decode((string) $raw, true);
    return is_array($data) ? $data : array();
}

function upsert_contact($email, $first, $last, $company)
{
    $body = array('locationId' => LOC, 'email' => $email, 'source' => 'Website');
    if ($first !== '') $body['firstName'] = $first;
    if ($last !== '') $body['lastName'] = $last;
    if ($company !== '') $body['companyName'] = $company;
    $r = ghl('POST', '/contacts/upsert', $body);
    $c = isset($r['contact']) ? $r['contact'] : array();
    if (empty($c['id'])) throw new RuntimeException('upsert: no contact id');
    return $c;
}

function get_contact($id)
{
    $r = ghl('GET', '/contacts/' . rawurlencode($id));
    return isset($r['contact']) ? $r['contact'] : array();
}

function field_value($contact, $fieldId)
{
    foreach ((isset($contact['customFields']) ? $contact['customFields'] : array()) as $f) {
        if (isset($f['id']) && $f['id'] === $fieldId) {
            $v = isset($f['value']) ? $f['value'] : (isset($f['field_value']) ? $f['field_value'] : '');
            return is_string($v) ? trim($v) : '';
        }
    }
    return '';
}

function set_field($contactId, $fieldId, $value)
{
    ghl('PUT', '/contacts/' . rawurlencode($contactId), array(
        'customFields' => array(array('id' => $fieldId, 'field_value' => $value)),
    ));
}

function add_note($contactId, $text)
{
    ghl('POST', '/contacts/' . rawurlencode($contactId) . '/notes', array('body' => $text));
}

function add_tags($contactId, $tags)
{
    ghl('POST', '/contacts/' . rawurlencode($contactId) . '/tags', array('tags' => array_values($tags)));
}

/* Upload a PDF into a Media Storage folder; returns its public URL. */
function upload_pdf($bytes, $filename, $folder)
{
    $tmp = tempnam(sys_get_temp_dir(), 'oyss');
    file_put_contents($tmp, $bytes);
    try {
        $r = ghl('POST', '/medias/upload-file', null, array(
            'file'     => new CURLFile($tmp, 'application/pdf', $filename),
            'name'     => $filename,
            'hosted'   => 'false',
            'parentId' => $folder,
        ));
    } finally {
        @unlink($tmp);
    }
    $url = isset($r['url']) ? $r['url'] : (isset($r['fileUrl']) ? $r['fileUrl'] : '');
    if ($url === '') throw new RuntimeException('upload: no url in ' . substr(json_encode($r), 0, 200));
    return $url;
}

function send_email($contactId, $subject, $html, $attachments)
{
    return ghl('POST', '/conversations/messages', array(
        'type'        => 'Email',
        'contactId'   => $contactId,
        'subject'     => $subject,
        'html'        => $html,
        'attachments' => array_values($attachments),
        'emailBcc'    => array(STUDIO_INBOX),
    ));
}

/* ------------------------------------------------------------ helpers */

function h($s)
{
    return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8');
}

function clean($v, $max)
{
    $v = trim(preg_replace('/[\x00-\x1F\x7F]+/u', ' ', (string) $v));
    return function_exists('mb_substr') ? mb_substr($v, 0, $max, 'UTF-8') : substr($v, 0, $max);
}

function local_date($iso, $withTime = false)
{
    try {
        $d = new DateTime($iso);
    } catch (Exception $e) {
        $d = new DateTime('now');
    }
    $d->setTimezone(new DateTimeZone(TZ));
    return $d->format($withTime ? 'F j, Y, g:i A T' : 'F j, Y');
}

function money($amount, $currency)
{
    $cur = strtoupper($currency ?: 'USD');
    $sym = array('USD' => '$', 'CAD' => 'CA$', 'AUD' => 'A$', 'EUR' => "\u{20AC}", 'GBP' => "\u{00A3}");
    return (isset($sym[$cur]) ? $sym[$cur] : '') . number_format((float) $amount, 2) . ' ' . $cur;
}

/* ------------------------------------------------------------ emails */

function email_shell($inner, $footer)
{
    return '<div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;color:#2E2E2E">' .
        '<p style="margin:0 0 6px;font:700 13px/1.4 Arial,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#2E2E2E">Own Your Stage Studio</p>' .
        '<p style="margin:0 0 26px;width:36px;height:3px;background:#B91C1C;font-size:0;line-height:0">&nbsp;</p>' .
        $inner .
        '<p style="margin:26px 0 0;font:16px/1.6 Georgia,serif">Annette Knecht Seier<br>Founder, Own Your Stage Studio</p>' .
        '<p style="margin:30px 0 0;font:12px/1.5 Arial,sans-serif;color:#5B5552">' . $footer . '</p>' .
        '</div>';
}

function p($html)
{
    return '<p style="margin:0 0 16px;font:16px/1.6 Georgia,serif">' . $html . '</p>';
}

function kicker($text)
{
    return '<p style="margin:26px 0 8px;font:700 12px/1.4 Arial,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:#B91C1C">' . h($text) . '</p>';
}

function agreement_email($d, $withReceipt)
{
    $first = $d['first_name'] !== '' ? $d['first_name'] : 'there';
    $inner = p('Hi ' . h($first) . ',') .
        p('Your signed copy of the <b>' . h($d['agreement']) . '</b> is attached to this email as a PDF. ' .
          'It holds the full agreement, the signing record and your signature. Please keep it for your records.') .
        ($withReceipt ? p('Your payment receipt is attached as well, so you have both documents together.') : '') .
        kicker('The signing record') .
        p('Signed by <b>' . h($d['legal_name']) . '</b>' . ($d['business_name'] !== '' ? ' for ' . h($d['business_name']) : '') .
          ' on ' . h($d['signedAtDisplay']) . '.' .
          ($d['agreement_version'] !== '' ? ' Text version ' . h($d['agreement_version']) . '.' : ''));
    if ($d['signed_copy_url'] !== '') {
        $inner .= p('You can also open the signed copy on the website at any time:') .
            '<p style="margin:10px 0 18px"><a href="' . h($d['signed_copy_url']) . '" style="display:inline-block;border:2px solid #B91C1C;color:#B91C1C;text-decoration:none;font:700 15px Arial,sans-serif;padding:12px 24px;border-radius:2px">Open your signed agreement</a></p>';
    }
    $AG = agreements();
    $meta = isset($AG[$d['agreement']]) ? $AG[$d['agreement']] : null;
    if ($meta && $withReceipt) {
        $inner .= kicker('What happens next') . p('Your payment is received, thank you. ' . h($meta['next']));
    } elseif ($meta) {
        $inner .= kicker('The last step') . p(h($meta['pay_intro']));
        foreach ($meta['pay'] as $i => $b) {
            $inner .= '<p style="margin:' . ($i ? '0' : '10px') . ' 0 18px"><a href="' . h($b[1]) . '" style="display:inline-block;' .
                ($i ? 'border:2px solid #B91C1C;color:#B91C1C;padding:12px 24px;' : 'background:#B91C1C;color:#fff;padding:14px 26px;') .
                'text-decoration:none;font:700 15px Arial,sans-serif;border-radius:2px">' . h($b[0]) . '</a></p>';
        }
        $inner .= p('If you have already paid, thank you, there is nothing more to do here. ' . h($meta['next']));
    }
    return email_shell($inner, 'You are receiving this because you signed the ' . h($d['agreement']) .
        ' at ownyourstagestudio.com. This email is your copy of the signed agreement.');
}

function receipt_rows($r)
{
    $rows = array(
        'Receipt number' => $r['number'],
        'Date paid'      => $r['date'],
        'Description'    => $r['description'],
        'Payment method' => $r['method'],
        'Amount paid'    => $r['amount'],
    );
    $html = '<table role="presentation" style="width:100%;border-collapse:collapse;margin:4px 0 18px;font:15px/1.5 Arial,sans-serif;color:#2E2E2E">';
    foreach ($rows as $k => $v) {
        if ($v === '') continue;
        $strong = $k === 'Amount paid';
        $html .= '<tr><td style="padding:9px 12px 9px 0;border-bottom:1px solid #E6E0DA;color:#5B5552;white-space:nowrap;vertical-align:top">' . h($k) . '</td>' .
                 '<td style="padding:9px 0;border-bottom:1px solid #E6E0DA;' . ($strong ? 'font-weight:700' : '') . '">' . h($v) . '</td></tr>';
    }
    return $html . '</table>';
}

function receipt_email($first, $r, $agreementName)
{
    $inner = p('Hi ' . h($first !== '' ? $first : 'there') . ',') .
        p('Thank you. Your payment has been received, and your receipt is attached to this email as a PDF.') .
        ($agreementName !== '' ? p('Your signed <b>' . h($agreementName) . '</b> is attached as well, so you have both documents together.') : '') .
        kicker('Receipt') . receipt_rows($r) .
        p('If anything on this receipt looks wrong, reply to this email and we will put it right.');
    return email_shell($inner, 'You are receiving this because you made a payment to Own Your Stage Studio, LLC. Keep this email for your records.');
}

/* ------------------------------------------------------------ receipts */

/* What the transaction says, in the words of a receipt. */
function receipt_facts($tx, $contact)
{
    $id = isset($tx['_id']) ? (string) $tx['_id'] : '';
    $when = isset($tx['createdAt']) ? $tx['createdAt'] : gmdate('c');
    $name = trim((isset($contact['firstName']) ? $contact['firstName'] : '') . ' ' . (isset($contact['lastName']) ? $contact['lastName'] : ''));
    if ($name === '' && !empty($tx['contactName'])) $name = $tx['contactName'];
    $email = !empty($contact['email']) ? $contact['email'] : (isset($tx['contactEmail']) ? $tx['contactEmail'] : '');

    $desc = '';
    foreach (array('entitySourceName') as $k) if (!empty($tx[$k]) && is_string($tx[$k])) $desc = $tx[$k];
    if ($desc === '' && !empty($tx['entitySourceMeta']) && is_array($tx['entitySourceMeta'])) {
        foreach (array('name', 'productName', 'title') as $k) {
            if (!empty($tx['entitySourceMeta'][$k]) && is_string($tx['entitySourceMeta'][$k])) { $desc = $tx['entitySourceMeta'][$k]; break; }
        }
    }
    if ($desc === '') $desc = 'Payment to Own Your Stage Studio';
    if (!empty($tx['subscriptionId'])) $desc .= ' (subscription payment)';

    /* the card, wherever this provider put it */
    $brand = ''; $last4 = '';
    $spots = array();
    if (!empty($tx['paymentMethod']) && is_array($tx['paymentMethod'])) $spots[] = $tx['paymentMethod'];
    if (!empty($tx['chargeSnapshot']) && is_array($tx['chargeSnapshot'])) {
        $cs = $tx['chargeSnapshot'];
        $spots[] = $cs;
        if (!empty($cs['payment_method_details']['card'])) $spots[] = $cs['payment_method_details']['card'];
        if (!empty($cs['source']) && is_array($cs['source'])) $spots[] = $cs['source'];
    }
    foreach ($spots as $s) {
        if (isset($s['card']) && is_array($s['card'])) $s = $s['card'];
        if ($brand === '' && !empty($s['brand']) && is_string($s['brand'])) $brand = $s['brand'];
        if ($last4 === '' && !empty($s['last4'])) $last4 = (string) $s['last4'];
    }
    $method = $brand !== '' ? ucwords(str_replace('_', ' ', $brand)) : 'Card';
    if ($last4 !== '') $method .= ' ending ' . $last4;

    $amount = isset($tx['amount']) ? (float) $tx['amount'] : 0.0;
    $refunded = isset($tx['amountRefunded']) ? (float) $tx['amountRefunded'] : 0.0;
    $cur = isset($tx['currency']) ? $tx['currency'] : 'USD';

    return array(
        'id'          => $id,
        'number'      => 'OYSS-' . (new DateTime($when))->setTimezone(new DateTimeZone(TZ))->format('Ymd') . '-' . strtoupper(substr($id, -6)),
        'date'        => local_date($when),
        'datetime'    => local_date($when, true),
        'name'        => $name,
        'email'       => $email,
        'description' => $desc,
        'method'      => $method,
        'amount'      => money($amount, $cur),
        'refunded'    => $refunded > 0 ? money($refunded, $cur) : '',
        'reference'   => $id,
    );
}

function receipt_pdf($r)
{
    $pdf = new MiniPdf('Receipt ' . $r['number'] . ' - Own Your Stage Studio');
    $RED = array(185, 28, 28); $DARK = array(31, 30, 29); $BODY = array(40, 38, 36); $MUTED = array(110, 104, 100);
    $M = 60; $R = MiniPdf::W - 60;

    $pdf->text($M, 72, 'OWN YOUR STAGE STUDIO, LLC', 9, true, $RED, 'left', 1.2);
    $pdf->box($M, 82, 36, 3, $RED);
    $pdf->text($M, 132, 'Receipt', 30, true, $DARK);
    $pdf->text($M, 156, 'Paid ' . $r['date'], 11.5, false, $MUTED);
    $pdf->text($R, 118, 'RECEIPT NUMBER', 7.5, true, $MUTED, 'right', 0.8);
    $pdf->text($R, 134, $r['number'], 11, true, $DARK, 'right');

    $y = 190;
    $pdf->line($M, $y, $R, $y, 0.8);
    $y += 30;
    $rows = array(
        array('BILLED TO', trim($r['name'] . "\n" . $r['email'])),
        array('DESCRIPTION', $r['description']),
        array('DATE PAID', $r['datetime']),
        array('PAYMENT METHOD', $r['method']),
        array('REFERENCE', $r['reference']),
        array('STATUS', $r['refunded'] !== '' ? 'Paid, ' . $r['refunded'] . ' since refunded' : 'Paid'),
    );
    foreach ($rows as $row) {
        $pdf->text($M, $y, $row[0], 7.5, true, $MUTED, 'left', 0.8);
        $lines = $pdf->wrap($row[1], 11, false, $R - 200);
        foreach ($lines as $i => $ln) $pdf->text(200, $y + $i * 16, $ln, 11, false, $BODY);
        $y += max(1, count($lines)) * 16 + 14;
    }

    $y += 6;
    $pdf->box($M, $y, $R - $M, 64, array(246, 243, 240));
    $pdf->box($M, $y, 3, 64, $RED);
    $pdf->text($M + 20, $y + 38, 'AMOUNT PAID', 8, true, $MUTED, 'left', 1);
    $pdf->text($R - 20, $y + 42, $r['amount'], 22, true, $DARK, 'right');

    $pdf->line($M, 716, $R, 716, 0.6);
    $pdf->text($M, 734, 'Own Your Stage Studio, LLC  ·  events@ownyourstagestudio.com  ·  ownyourstagestudio.com', 8, false, $MUTED);
    $pdf->text($M, 748, 'Thank you. This receipt confirms a payment received by Own Your Stage Studio, LLC.', 8, false, $MUTED);
    return $pdf->output();
}

/* Which side of the business a payment belongs to. */
function payment_line($tx)
{
    $hay = strtolower(json_encode(array(
        isset($tx['entitySourceName']) ? $tx['entitySourceName'] : '',
        isset($tx['entitySourceMeta']) ? $tx['entitySourceMeta'] : '',
    )));
    return strpos($hay, 'panelist') !== false ? 'panelist' : 'host';
}

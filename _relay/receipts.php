<?php
/* cron, every five minutes:  php -q /home/rogucmxm/oyss_private/receipts.php */
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require __DIR__ . '/lib.php';
require __DIR__ . '/receipts_job.php';
$r = run_receipts(in_array('--dry', $argv, true));
if (in_array('-v', $argv, true)) echo json_encode($r, JSON_PRETTY_PRINT), "\n";

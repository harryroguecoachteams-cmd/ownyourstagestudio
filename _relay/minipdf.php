<?php
/*
 * A one-page PDF writer for the payment receipts: US Letter, the two
 * standard Helvetica faces (nothing to embed), text, rules and filled
 * boxes. Coordinates are points from the TOP left, like the page reads.
 * Text is WinAnsi, so "·", "é" and the like print; anything else is dropped.
 */

final class MiniPdf
{
    const W = 612;
    const H = 792;

    /* Helvetica and Helvetica-Bold advance widths, ASCII 32..126 (AFM, /1000 em) */
    const HELV = '278,278,355,556,556,889,667,191,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,333,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584';
    const HELVB = '278,333,474,556,556,889,722,238,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,333,333,584,584,584,611,975,722,722,722,722,667,611,778,722,278,556,722,611,833,722,778,667,778,722,667,611,722,667,944,667,667,611,333,278,333,584,556,333,556,611,556,611,556,333,611,611,278,278,556,278,889,611,611,611,611,389,556,333,611,556,778,556,556,500,389,280,389,584';

    private $stream = '';
    private $widths = array();
    private $title = '';

    public function __construct($title = '')
    {
        $this->title = $title;
        $this->widths = array(
            false => array_map('intval', explode(',', self::HELV)),
            true  => array_map('intval', explode(',', self::HELVB)),
        );
    }

    /* UTF-8 in, WinAnsi bytes out */
    public static function ansi($s)
    {
        $s = strtr((string) $s, array(
            "\xE2\x80\x98" => "'", "\xE2\x80\x99" => "'", "\xE2\x80\x9C" => '"', "\xE2\x80\x9D" => '"',
            "\xE2\x80\x93" => '-', "\xE2\x80\x94" => '-', "\xC2\xA0" => ' ', "\xE2\x80\xA6" => '...',
        ));
        $t = function_exists('iconv') ? @iconv('UTF-8', 'Windows-1252//IGNORE', $s) : false;
        if ($t === false) $t = preg_replace('/[^\x20-\x7E]/', '', $s);
        return $t;
    }

    private static function esc($bytes)
    {
        return strtr($bytes, array('\\' => '\\\\', '(' => '\\(', ')' => '\\)', "\r" => '', "\n" => ' '));
    }

    /* width of a UTF-8 string, in points */
    public function width($s, $size, $bold = false)
    {
        $w = 0;
        $b = self::ansi($s);
        $tab = $this->widths[(bool) $bold];
        for ($i = 0, $n = strlen($b); $i < $n; $i++) {
            $c = ord($b[$i]);
            $w += ($c >= 32 && $c <= 126) ? $tab[$c - 32] : 556;
        }
        return $w * $size / 1000;
    }

    /* word wrap to a width; returns the lines */
    public function wrap($s, $size, $bold, $maxw)
    {
        $out = array();
        foreach (preg_split('/\R/', (string) $s) as $para) {
            $line = '';
            foreach (preg_split('/\s+/', trim($para)) as $word) {
                if ($word === '') continue;
                $try = $line === '' ? $word : $line . ' ' . $word;
                if ($line !== '' && $this->width($try, $size, $bold) > $maxw) {
                    $out[] = $line;
                    $line = $word;
                } else {
                    $line = $try;
                }
            }
            $out[] = $line;
        }
        return $out;
    }

    private static function rgb($c)
    {
        return sprintf('%.3F %.3F %.3F', $c[0] / 255, $c[1] / 255, $c[2] / 255);
    }

    /* $y is the BASELINE, measured from the top */
    public function text($x, $y, $s, $size, $bold = false, $color = array(40, 38, 36), $align = 'left', $track = 0)
    {
        if ($align === 'right') $x -= $this->width($s, $size, $bold) + $track * max(0, strlen(self::ansi($s)) - 1);
        $this->stream .= sprintf("BT /%s %.2F Tf %s rg %.2F Tc %.2F %.2F Td (%s) Tj ET\n",
            $bold ? 'F2' : 'F1', $size, self::rgb($color), $track, $x, self::H - $y, self::esc(self::ansi($s)));
    }

    public function line($x1, $y1, $x2, $y2, $w = 0.6, $color = array(214, 208, 203))
    {
        $this->stream .= sprintf("%s RG %.2F w %.2F %.2F m %.2F %.2F l S\n",
            self::rgb($color), $w, $x1, self::H - $y1, $x2, self::H - $y2);
    }

    public function box($x, $y, $w, $h, $color)
    {
        $this->stream .= sprintf("%s rg %.2F %.2F %.2F %.2F re f\n",
            self::rgb($color), $x, self::H - $y - $h, $w, $h);
    }

    public function output()
    {
        $objs = array();
        $objs[1] = '<< /Type /Catalog /Pages 2 0 R >>';
        $objs[2] = '<< /Type /Pages /Kids [3 0 R] /Count 1 >>';
        $objs[3] = '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ' . self::W . ' ' . self::H . '] ' .
                   '/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>';
        $body = function_exists('gzcompress') ? gzcompress($this->stream, 9) : $this->stream;
        $objs[4] = '<< /Length ' . strlen($body) . ($body !== $this->stream ? ' /Filter /FlateDecode' : '') .
                   " >>\nstream\n" . $body . "\nendstream";
        $objs[5] = '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>';
        $objs[6] = '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>';
        $objs[7] = '<< /Title (' . self::esc(self::ansi($this->title)) . ') /Producer (Own Your Stage Studio) ' .
                   '/CreationDate (D:' . gmdate('YmdHis') . "Z) >>";

        $pdf = "%PDF-1.4\n%\xE2\xE3\xCF\xD3\n";
        $offsets = array();
        foreach ($objs as $n => $o) {
            $offsets[$n] = strlen($pdf);
            $pdf .= $n . " 0 obj\n" . $o . "\nendobj\n";
        }
        $xref = strlen($pdf);
        $pdf .= "xref\n0 " . (count($objs) + 1) . "\n0000000000 65535 f \n";
        foreach ($offsets as $off) $pdf .= sprintf("%010d 00000 n \n", $off);
        $pdf .= "trailer\n<< /Size " . (count($objs) + 1) . " /Root 1 0 R /Info 7 0 R >>\nstartxref\n" . $xref . "\n%%EOF\n";
        return $pdf;
    }
}

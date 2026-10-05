param([string]$page)
$p = "F:\Annette\own your studio\oyss-site\_ghl_native\pages\$page.html"
$t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8) -replace "`r`n", "`n"
Set-Clipboard -Value $t
$c = Get-Clipboard -Raw
"$page file $($t.Length) clip $($c.Length) editor-last-line $(($t -split "`n").Count) match $($t -eq $c)"

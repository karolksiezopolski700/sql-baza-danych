#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<?php

parse_str($_SERVER['QUERY_STRING'],$_GET);

$program = $_GET["program"];

if ($program == "program1") {
    include("tabela.cgi");
} elseif ($program == "program2") {
    include("dodawanie.cgi");
} elseif ($program == "program3") {
    include("dod_galeria.cgi");
} elseif ($program == "program4") {
    include("polozenie.cgi");
} elseif ($program == "program5") {
    include("ekspozycje.cgi");   
} elseif ($program == "program6") {
    include("wypozyczenia.cgi");      
} else {
    echo("nie dziala");
}
?>


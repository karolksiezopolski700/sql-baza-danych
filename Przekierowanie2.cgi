#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<?php

parse_str($_SERVER['QUERY_STRING'],$_GET);

$wybor = $_GET["wybor"];

if ($wybor == "pracownik") {
    include("formularz1.cgi");
} elseif ($wybor == "zwiedzajacy") {
    include("zwiedzanie.cgi");      
} else {
    echo("nie dziala");
}
?>


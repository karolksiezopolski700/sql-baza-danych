#!/usr/bin/php
<?php

$validUsername = "admin";
$validPassword = "pracownik123";

parse_str($_SERVER['QUERY_STRING'],$_GET);

$username = $_GET["username"];
$password = $_GET["password"];

if ($username === $validUsername && $password === $validPassword){
	echo("Status: 302 Found\n");
	echo("Location: strona_muzeum.cgi\n");
} else {
	echo("Status: 302 Found\n");
	echo("Location: failure.cgi\n");
}

echo("Content-type: text/html\n\n");


?>

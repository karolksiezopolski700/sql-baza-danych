#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
<title>Dodawanie galerii</title>
<meta charset="UTF-8">
</head>
<body bgcolor="white">
<h1>Podaj nazwe galerii</h1>
<form action="dod_galeria.cgi" method="GET">
    Nazwa Galerii: <INPUT TYPE="text" NAME="nazwa_galeria" VALUE="" SIZE=30 MAXLENGTH=30><br>
	<input type="submit" value="Dodaj">
</form>

<form action="strona_muzeum.cgi" method="GET">
    <input type="submit" value="Powrot na strone glowna Muzeum">
</form>

<?php

function konwertujNaNull($wartosc) { //zmienia "" na NULL
    return $wartosc === "" ? NULL : $wartosc;
}

parse_str($_SERVER['QUERY_STRING'],$_GET);

$link = pg_connect("host=lkdb dbname=mrbd user=kk438801 password=karol321");

$_GET = array_map('konwertujNaNull', $_GET); //zmienia "" na NULL

$nazwa = $_GET["nazwa_galeria"];

$query= "INSERT INTO Galerie VALUES($1, $2)";

$ileG = pg_query($link, "SELECT COUNT(*) AS ile FROM Galerie");
$temp = pg_fetch_array($ileG, 0)["ile"] + 1;
$next_id = (string) $temp;

$dodaj = pg_query_params($link, $query, array($next_id, $nazwa));

$result = pg_query($link, "SELECT * FROM Galerie");
$numrows = pg_numrows($result);
?>

<h2 align=center>Galerie</h2>

<table border="1" align=center>
<tr>
 <th>ID</th>	
 <th>Nazwa</th>
</tr>
<?php

 // Przechodzimy po wierszach wyniku.
 for($ri = 0; $ri < $numrows; $ri++) {
  echo "<tr>\n";
  $row = pg_fetch_array($result, $ri);
  echo " <td>" . $row["id_galeria"] . "</td>\n";
  echo " <td>" . $row["nazwa_galeria"] . "</td>
 </tr>
";
 }
?> 
</table>


<?php
 pg_close($link);
?>
</table>
</body>
</html>

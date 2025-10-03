#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
<title>Ekspozycje</title>
<meta charset="UTF-8">
</head>
<body bgcolor="white">
<h1>Podaj ekspozycje i wybierz nowa date</h1>
<form action="ekspozycje.cgi" method="GET">
    ID Ekspozycji: <INPUT TYPE="text" NAME="id_ekspozycja" VALUE="" SIZE=30 MAXLENGTH=30><br>
    Nowa data początku ekspozycji: <INPUT TYPE="date" NAME="data_pocz" VALUE="" SIZE=30 MAXLENGTH=30><br>
    Nowa data końca ekspozycji: <INPUT TYPE="date" NAME="data_kon" VALUE="" SIZE=30 MAXLENGTH=30><br>
	<input type="submit" value="Zmien">
</form>

<form action="strona_muzeum.cgi" method="GET">
    <input type="submit" value="Powrot na strone glowna Muzeum">
</form>

<?php

function konwertujNaNull($wartosc) { //zmienia "" na NULL
    return $wartosc === "" ? NULL : $wartosc;
}

parse_str($_SERVER['QUERY_STRING'],$_GET);

$link = pg_connect("host=localhost dbname=twoja_baza user=twoj_user password=twoje_haslo");

$_GET = array_map('konwertujNaNull', $_GET); //zmienia "" na NULL

$id_ekspozycja = $_GET["id_ekspozycja"];
$data_pocz = $_GET["data_pocz"];
$data_kon = $_GET["data_kon"];

$query= "UPDATE Ekspozycje SET data_pocz = $1, data_kon = $2 WHERE id_ekspozycja = $3";

$zmiana = pg_query_params($link, $query, array($data_pocz, $data_kon, $id_ekspozycja));

$result = pg_query($link, "SELECT * FROM Ekspozycje");
$numrows = pg_numrows($result);
?>

<h2 align=center>Ekspozycje</h2>

<table border="1" align=center>
<tr>
 <th>ID Ekspozycji</th>	
 <th>ID Eksponatu</th>
 <th>ID Galerii</th>
 <th>Sala</th>
 <th>Data początku ekspozycji</th>
 <th>Data końca ekspozycji</th>
</tr>
<?php

 // Przechodzimy po wierszach wyniku.
 for($ri = 0; $ri < $numrows; $ri++) {
  echo "<tr>\n";
  $row = pg_fetch_array($result, $ri);
  echo " <td>" . $row["id_ekspozycja"] . "</td>\n";
  echo " <td>" . $row["id_eksponat"] . "</td>\n";
  echo " <td>" . $row["id_galeria"] . "</td>\n";
  echo " <td>" . $row["sala"] . "</td>\n";
  echo " <td>" . $row["data_pocz"] . "</td>\n";
  echo " <td>" . $row["data_kon"] . "</td>
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

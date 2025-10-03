#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
<title>Wypozyczenia</title>
<meta charset="UTF-8">
</head>
<body bgcolor="white">
<h1>Podaj wypozyczenie i wybierz nowa date</h1>
<form action="wypozyczenia.cgi" method="GET">
    ID Wypozyczenia: <INPUT TYPE="text" NAME="id_wypozyczenie" VALUE="" SIZE=30 MAXLENGTH=30><br>
    Nowa data początku wypozyczenia: <INPUT TYPE="date" NAME="data_wypo" VALUE="" SIZE=30 MAXLENGTH=30><br>
    Nowa data końca wypozyczenia: <INPUT TYPE="date" NAME="data_zwro" VALUE="" SIZE=30 MAXLENGTH=30><br>
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

$link = pg_connect("host=lkdb dbname=mrbd user=kk438801 password=karol321");

$_GET = array_map('konwertujNaNull', $_GET); //zmienia "" na NULL

$id_wypozyczenie = $_GET["id_wypozyczenie"];
$data_wypo = $_GET["data_wypo"];
$data_zwro = $_GET["data_zwro"];

$query= "UPDATE Wypozyczenia SET data_wypo = $1, data_zwro = $2 WHERE id_wypozyczenie = $3";

$zmiana = pg_query_params($link, $query, array($data_wypo, $data_zwro, $id_wypozyczenie));

$result = pg_query($link, "SELECT * FROM Wypozyczenia");
$numrows = pg_numrows($result);
?>

<h2 align=center>Wypozyczenia</h2>

<table border="1" align=center>
<tr>
 <th>ID Wypozyczenia</th>	
 <th>ID Eksponatu</th>
 <th>ID Instytucji</th>
 <th>Nazwa Instytucji</th>
 <th>Miasto</th>
 <th>Data poczatku wypozyczenia</th>
 <th>Data końca wypozyczenia</th>
</tr>
<?php

 // Przechodzimy po wierszach wyniku.
 for($ri = 0; $ri < $numrows; $ri++) {
  echo "<tr>\n";
  $row = pg_fetch_array($result, $ri);
  echo " <td>" . $row["id_wypozyczenie"] . "</td>\n";
  echo " <td>" . $row["id_eksponat"] . "</td>\n";
  echo " <td>" . $row["id_instytucja"] . "</td>\n";
  echo " <td>" . $row["nazwa"] . "</td>\n";
  echo " <td>" . $row["miasto"] . "</td>\n";
  echo " <td>" . $row["data_wypo"] . "</td>\n";
  echo " <td>" . $row["data_zwro"] . "</td>
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

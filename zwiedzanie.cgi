#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
<title>Zwiedzajacy</title>
</head>
<body bgcolor="white">
<h1>Wyszukaj artyste</h1>
<form action="zwiedzanie.cgi" method="GET"> 
	<INPUT TYPE="text" NAME="art" VALUE="" SIZE=30 MAXLENGTH=46><br>
	<input type="submit" value="Szukaj">
</form>

<form action="zwiedzanie.cgi" method="GET"> 
	<input type="submit" value="Pokaz wszystkie eksponaty"> 
</form>

<?php

parse_str($_SERVER['QUERY_STRING'],$_GET);

$link = pg_connect("host=localhost dbname=twoja_baza user=twoj_user password=twoje_haslo");

$art = $_GET["art"];
$pattern = "%" . $art . "%";
if($art === ""){
	$result = pg_query($link, "SELECT
     e.tytul AS tytul,
     CASE
         WHEN g.nazwa_galeria IS NOT NULL THEN
             'Ekspozycja: ' || g.nazwa_galeria || ', ' || ex.sala
         WHEN w.id_instytucja IS NOT NULL THEN
             'Wypozyczony: ' || w.nazwa || ', ' || w.miasto
         ELSE
             'Magazyn'
     END AS status,
     CONCAT(a.imie, ' ', a.nazwisko) AS artysta, e.do_wypozyczenia AS do_wypozyczenia 
 FROM
     Eksponaty e
 LEFT JOIN
     Ekspozycje ex ON e.id_eksponat = ex.id_eksponat
                   AND (ex.data_kon IS NULL OR ex.data_kon > CURRENT_DATE)
 LEFT JOIN
     Galerie g ON ex.id_galeria = g.id_galeria
 LEFT JOIN
     Wypozyczenia w ON e.id_eksponat = w.id_eksponat
                    AND (w.data_zwro IS NULL OR w.data_zwro > CURRENT_DATE) 
 LEFT JOIN 
	 Artysci a ON e.id_artysta = a.id_artysta");
}else{
	$pattern = "%" . $art . "%";
	$query = "SELECT
     e.tytul AS tytul,
     CASE
         WHEN g.nazwa_galeria IS NOT NULL THEN
             'Ekspozycja: ' || g.nazwa_galeria || ', ' || ex.sala
         WHEN w.id_instytucja IS NOT NULL THEN
             'Wypozyczony: ' || w.nazwa || ', ' || w.miasto
         ELSE
             'Magazyn'
     END AS status,
     CONCAT(a.imie, ' ', a.nazwisko) AS artysta, e.do_wypozyczenia AS do_wypozyczenia 
 FROM
     Eksponaty e
 LEFT JOIN
     Ekspozycje ex ON e.id_eksponat = ex.id_eksponat
                   AND (ex.data_kon IS NULL OR ex.data_kon > CURRENT_DATE)
 LEFT JOIN
     Galerie g ON ex.id_galeria = g.id_galeria
 LEFT JOIN
     Wypozyczenia w ON e.id_eksponat = w.id_eksponat
                    AND (w.data_zwro IS NULL OR w.data_zwro > CURRENT_DATE) 
 LEFT JOIN 
	 Artysci a ON e.id_artysta = a.id_artysta 
	 WHERE CONCAT(imie, ' ', nazwisko) LIKE $1";
	$result = pg_query_params($link, $query, array($pattern));
}
$numrows = pg_numrows($result);
?>

<h2 align=center>Eksponaty</h2>

<table border="1" align=center>
<tr>
 <th>Tytul</th>
 <th>Status</th>
 <th>Artysta</th>
 <th>Czy do wypozyczenia</th>
</tr>
<?php

 for($ri = 0; $ri < $numrows; $ri++) {
  echo "<tr>\n";
  $row = pg_fetch_array($result, $ri);
  echo " <td>" . $row["tytul"] . "</td>\n";
  echo " <td>" . $row["status"] . "</td>\n";
  echo " <td>" . $row["artysta"] . "</td>\n";
  echo " <td>" . $row["do_wypozyczenia"] . "</td>
 </tr>
";
 }
 pg_close($link);
?>
</table>
</body>
</html>

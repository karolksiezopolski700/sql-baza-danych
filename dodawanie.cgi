#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
<title>Dodawanie eksponatow</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>
    function toggleFields() {
        const isChecked = document.getElementById("thisbox").checked;
       
        // Pokaż/ukryj pola związane z artystą
        document.getElementById("artystaFields").style.display = isChecked ? "none" : "block";
       
        // Pokaż/ukryj pole ID artysty
        document.getElementById("idArtystyField").style.display = isChecked ? "block" : "none";
    }
</script>
</head>
<body bgcolor="white">
<h1>Podaj informacje o eksponacie i artyscie</h1>
<form action="dodawanie.cgi" method="GET">
    Tytul: <INPUT TYPE="text" NAME="tytul" VALUE="" SIZE=30 MAXLENGTH=40><br>
    Typ: <INPUT TYPE="text" NAME="typ" VALUE="" SIZE=30 MAXLENGTH=20><br>
    Wysokosc: <INPUT TYPE="number" NAME="wysokosc" VALUE="" SIZE=30 MAXLENGTH=20><br>
    Szerokosc: <INPUT TYPE="number" NAME="szerokosc" VALUE="" SIZE=30 MAXLENGTH=20><br>
    Waga: <INPUT TYPE="number" NAME="waga" VALUE="" SIZE=30 MAXLENGTH=15><br>

    <!-- Pola do wpisywania danych artysty -->
    <div id="artystaFields">
        Imie artysty: <INPUT TYPE="text" NAME="imie" VALUE="" SIZE=30 MAXLENGTH=30><br>
        Nazwisko artysty: <INPUT TYPE="text" NAME="nazwisko" VALUE="" SIZE=30 MAXLENGTH=20><br>
        Rok urodzenia artysty: <INPUT TYPE="number" NAME="rok_urodzenia" VALUE="" SIZE=30 MAXLENGTH=20><br>
        Rok smierci arysty: <INPUT TYPE="number" NAME="rok_smierci" VALUE="" SIZE=30 MAXLENGTH=20><br>
    </div>

    <!-- Checkbox kontrolujący widoczność -->
    Artysta jest juz w bazie
    <INPUT TYPE="checkbox" ID="thisbox" NAME="thisbox" VALUE="tak" onchange="toggleFields()"><br>

    <!-- Pole do wpisania ID artysty -->
    <div id="idArtystyField" style="display: none;">
        ID Artysty: <INPUT TYPE="text" NAME="id_artysta" VALUE="" SIZE=30 MAXLENGTH=5><br>
    </div>

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

$czy_w_bazie = $_GET["thisbox"];

$tytul = $_GET["tytul"];
$typ = $_GET["typ"];
$wysokosc = $_GET["wysokosc"];
$szerokosc = $_GET["szerokosc"];
$waga = $_GET["waga"];
$imie = $_GET["imie"];
$nazwisko = $_GET["nazwisko"];
$rok_urodzenia = $_GET["rok_urodzenia"];
$rok_smierci = $_GET["rok_smierci"];
$id_artysta = $_GET["id_artysta"];

$query_art = "INSERT INTO Artysci VALUES($1, $2, $3, $4, $5)";
$query_eksp = "INSERT INTO Eksponaty VALUES($1, $2, $3, $4, $5, $6, $7, $8)";

$ile_art = pg_query($link, "SELECT COUNT(*) AS ile_a FROM Artysci");
$ile_eksp = pg_query($link, "SELECT COUNT(*) AS ile_e FROM Eksponaty");
$temp = pg_fetch_array($ile_eksp, 0)["ile_e"] + 1;
$next_id_eksp = (string) $temp;
$temp = pg_fetch_array($ile_art, 0)["ile_a"] + 1;
$next_id_art = (string) $temp;

$query_czy_w_bazie = "SELECT COUNT(*) AS ile FROM Artysci WHERE id_artysta = $1";
$sprawdz = pg_query_params($link, $query_czy_w_bazie, array($id_artysta));
$warunek = pg_fetch_array($sprawdz, 0)["ile"];


if($czy_w_bazie == "tak" && $id_artysta != NULL){
	$dodaj = pg_query_params($link, $query_eksp, array($next_id_eksp, $tytul, $typ, $wysokosc, $szerokosc, $waga, $id_artysta, 'tak'));
	}
else{
	if($tytul!=NULL && $typ!=NULL && $wysokosc!=NULL && $szerokosc!=NULL && $waga!=NULL){
		$dodaj = pg_query_params($link, $query_art, array($next_id_art, $imie, $nazwisko, $rok_urodzenia, $rok_smierci));
		$dodaj = pg_query_params($link, $query_eksp, array($next_id_eksp, $tytul, $typ, $wysokosc, $szerokosc, $waga, $next_id_art, 'tak'));
		}
	}

$result = pg_query($link, "SELECT * FROM Eksponaty");
$numrows = pg_numrows($result);
?>

<h2 align=center>Eksponaty</h2>

<table border="1" align=center>
<tr>
 <th>ID</th>	
 <th>Tytul</th>
 <th>Typ</th>
 <th>Wysokosc</th>
 <th>Szerokosc</th>
 <th>Waga</th>
 <th>ID Artysty</th>
 <th>Czy do wypozyczenia</th>
</tr>
<?php

 // Przechodzimy po wierszach wyniku.
 for($ri = 0; $ri < $numrows; $ri++) {
  echo "<tr>\n";
  $row = pg_fetch_array($result, $ri);
  echo " <td>" . $row["id_eksponat"] . "</td>\n";
  echo " <td>" . $row["tytul"] . "</td>\n";
  echo " <td>" . $row["typ"] . "</td>\n";
  echo " <td>" . $row["wysokosc"] . "</td>\n";
  echo " <td>" . $row["szerokosc"] . "</td>\n";
  echo " <td>" . $row["waga"] . "</td>\n";
  echo " <td>" . $row["id_artysta"] . "</td>\n";
  echo " <td>" . $row["do_wypozyczenia"] . "</td>
 </tr>
";
 }
?> 
</table>

<?php
$result = pg_query($link, "SELECT * FROM Artysci");
$numrows = pg_numrows($result);
?>

<h2 align=center>Artysci</h2>

<table border="1" align=center>
<tr>
 <th>ID</th>	
 <th>Imie</th>
 <th>Nazwisko</th>
 <th>Rok urodzenia</th>
 <th>Rok Smierci</th>
</tr>

<?php

 // Przechodzimy po wierszach wyniku.
 for($ri = 0; $ri < $numrows; $ri++) {
  echo "<tr>\n";
  $row = pg_fetch_array($result, $ri);
  echo " <td>" . $row["id_artysta"] . "</td>\n";
  echo " <td>" . $row["imie"] . "</td>\n";
  echo " <td>" . $row["nazwisko"] . "</td>\n";
  echo " <td>" . $row["rok_urodzenia"] . "</td>\n";
  echo " <td>" . $row["rok_smierci"] . "</td>
 </tr>
";
 } 

 pg_close($link);
?>
</table>
</body>
</html>

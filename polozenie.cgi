#!/usr/bin/env php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
<title>Zmiana informacji o polozeniu eksponatow</title>
<script>
    function toggleRadioFields() {
        const magazynFields = document.getElementById("magazynFields");
        const ekspozycjaFields = document.getElementById("ekspozycjaFields");
        const wypozyczenieFields = document.getElementById("wypozyczenieFields");

        const selectedOption = document.querySelector('input[name="akcja"]:checked').value;

        // Sterowanie widocznością pól
        magazynFields.style.display = (selectedOption === "magazyn") ? "block" : "none";
        ekspozycjaFields.style.display = (selectedOption === "ekspozycja") ? "block" : "none";
        wypozyczenieFields.style.display = (selectedOption === "wypozyczenie") ? "block" : "none";
    }
</script>
</head>
<body bgcolor="white">
<h3>Wybierz czynnosc:</h3>
<input type="radio" id="magazyn" name="akcja" value="magazyn" onchange="toggleRadioFields()" checked>
<label for="magazyn">Przenies do magazynu</label><br>

<input type="radio" id="ekspozycja" name="akcja" value="ekspozycja" onchange="toggleRadioFields()">
<label for="ekspozycja">Dodaj ekspozycje</label><br>

<input type="radio" id="wypozyczenie" name="akcja" value="wypozyczenie" onchange="toggleRadioFields()">
<label for="wypozyczenie">Dodaj wypozyczenie</label><br>

<form action="polozenie.cgi" method="GET">
	ID Eksponatu: <input type="text" name="id_eksponat" value="" size="30" maxlength="5"><br>
	<!-- Sekcja dla "Przenieś do magazynu" -->
	<div id="magazynFields" style="display: block;">
		Przenies do magazynu <INPUT TYPE="checkbox" ID="thisbox" NAME="thisbox" VALUE="tak"><br>
	</div>

	<!-- Sekcja dla "Dodaj ekspozycję" -->
	<div id="ekspozycjaFields" style="display: none;">
		ID Galerii: <input type="text" name="id_galeria" value="" size="30" maxlength="30"><br>
		Sala: <input type="text" name="sala" value="" size="30" maxlength="20"><br>
		Data rozpoczecia: <input type="date" name="data_pocz"><br>
		Data zakonczenia: <input type="date" name="data_kon"><br>
	</div>

	<!-- Sekcja dla "Dodaj wypożyczenie" -->
	<div id="wypozyczenieFields" style="display: none;">
		Nazwa instytucji: <input type="text" name="nazwa" value="" size="30" maxlength="30"><br>
		Miasto: <input type="text" name="miasto" value="" size="30" maxlength="25"><br>
		Data wypozyczenia: <input type="date" name="data_wypo"><br>
		Data zwrotu: <input type="date" name="data_zwro"><br>
	</div>
	<input type="submit" value="Przenies">
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

$czy_do_magazynu = $_GET["thisbox"];

$id_eksponat = $_GET["id_eksponat"];
$id_galeria = $_GET["id_galeria"];
$sala = $_GET["sala"];
$data_pocz = $_GET["data_pocz"];
$data_kon = $_GET["data_kon"];
$nazwa = $_GET["nazwa"];
$miasto = $_GET["miasto"];
$data_wypo = $_GET["data_wypo"];
$data_zwro = $_GET["data_zwro"];

$ile_exp = pg_query($link, "SELECT COUNT(*) AS ile_ex FROM Ekspozycje");
$ile_wyp = pg_query($link, "SELECT COUNT(*) AS ile_w FROM Wypozyczenia");
$temp = pg_fetch_array($ile_exp, 0)["ile_ex"] + 1;
$next_id_exp = (string) $temp;
$temp = pg_fetch_array($ile_wyp, 0)["ile_w"] + 1;
$next_id_wyp = (string) $temp;

$temp_query = "SELECT id_instytucja FROM Wypozyczenia WHERE nazwa=$1";
$czy_ins = pg_query_params($link, $temp_query, array($nazwa));
$warunek = pg_fetch_array($czy_ins, 0)["id_instytucja"];


//USTALENIE ID INSTYTUCJI
if($warunek!=""){
	$id_instytucja = $warunek;
	}else{
		$temp_query2 = pg_query($link, "WITH Ile_wy AS (SELECT DISTINCT id_instytucja FROM Wypozyczenia) SELECT COUNT(*) AS ile_i FROM Ile_wy");
		$temp2 = pg_fetch_array($temp_query2, 0)["ile_i"] + 1;
		$id_instytucja = (string) $temp2;
		}
//AKTUALNY STATUS EKSPONATU

$query_status = "WITH Eks_status AS (SELECT
	 e.id_eksponat AS id_eksponat, 
     e.tytul AS tytul,
     CASE
         WHEN g.nazwa_galeria IS NOT NULL THEN
             'Ekspozycja: ' || g.nazwa_galeria || ', ' || ex.sala
         WHEN w.id_instytucja IS NOT NULL THEN
             'Wypozyczony: ' || w.nazwa || ', ' || w.miasto
         ELSE
             'Magazyn'
     END AS status 
 FROM
     Eksponaty e
 LEFT JOIN
     Ekspozycje ex ON e.id_eksponat = ex.id_eksponat
                   AND (ex.data_kon IS NULL OR ex.data_kon > CURRENT_DATE)
 LEFT JOIN
     Galerie g ON ex.id_galeria = g.id_galeria
 LEFT JOIN
     Wypozyczenia w ON e.id_eksponat = w.id_eksponat
                    AND (w.data_zwro IS NULL OR w.data_zwro > CURRENT_DATE)) SELECT status FROM Eks_status WHERE id_eksponat = $1";
$r_status = pg_query_params($link, $query_status, array($id_eksponat));
$stat = pg_fetch_array($r_status, 0)["status"][0];

if($id_eksponat!=NULL){
	if(($id_galeria==NULL || $sala==NULL || $data_pocz==NULL) && ($nazwa==NULL || $miasto==NULL || $data_wypo==NULL)){ //MAGAZYN
		}elseif($id_galeria!=NULL && $sala!=NULL && $data_pocz!=NULL){ //EKSPOZYCJA
			$query = "INSERT INTO Ekspozycje VALUES($1, $2, $3, $4, $5, $6)";
			$dodaj = pg_query_params($link, $query, array($next_id_exp, $id_eksponat, $id_galeria, $sala, $data_pocz, $data_kon));
			}elseif($nazwa!=NULL && $miasto!=NULL && $data_wypo!=NULL){//WYPOZYCZENIE
				$query = "INSERT INTO Wypozyczenia VALUES($1, $2, $3, $4, $5, $6,$7)";
				$dodaj = pg_query_params($link, $query, array($next_id_wyp, $id_eksponat, $id_instytucja, $nazwa, $miasto, $data_wypo, $data_zwro));
				}
	}
if($dodaj){// NIE KONCZ JESLI NIE DODANO NOWEGO
	if($stat=="E"){//ZAKONCZENIE OSTATNIEGO STATUSU
			$update_query = "
			UPDATE Ekspozycje
			SET data_kon = $1
			WHERE id_eksponat = $2
			  AND (
				  data_kon IS NULL
				  OR data_kon = (
					  SELECT MAX(data_kon)
					  FROM Ekspozycje
					  WHERE id_eksponat = $2
				  )
			  )";
			$update = pg_query_params($link, $update_query, array($data_pocz, $id_eksponat));
			} elseif($stat=="W"){
				$update_query = "
				UPDATE Wypozyczenia
				SET data_zwro = $1
				WHERE id_eksponat = $2
				  AND (
					  data_zwro IS NULL
					  OR data_zwro = (
						  SELECT MAX(data_zwro)
						  FROM Wypozyczenia
						  WHERE id_eksponat = $2
					  )
				  )";
				$update = pg_query_params($link, $update_query, array($data_wypo, $id_eksponat));
				}
}elseif($czy_do_magazynu == "tak" && $stat == "E"){
			$update_query = "
			UPDATE Ekspozycje
			SET data_kon = CURRENT_DATE
			WHERE id_eksponat = $1
			  AND (
				  data_kon IS NULL
				  OR data_kon = (
					  SELECT MAX(data_kon)
					  FROM Ekspozycje
					  WHERE id_eksponat = $1
				  )
			  )";
			$update = pg_query_params($link, $update_query, array($id_eksponat));
			} elseif($czy_do_magazynu == "tak" && $stat == "W"){
				$update_query = "
				UPDATE Wypozyczenia
				SET data_zwro = CURRENT_DATE
				WHERE id_eksponat = $1
				  AND (
					  data_zwro IS NULL
					  OR data_zwro = (
						  SELECT MAX(data_zwro)
						  FROM Wypozyczenia
						  WHERE id_eksponat = $1
					  )
				  )";
				$update = pg_query_params($link, $update_query, array($id_eksponat));
				}		
	
?>

<?php

$link = pg_connect("host=lkdb dbname=mrbd user=kk438801 password=karol321");

$result_query = "SELECT
	 e.id_eksponat AS id_eksponat, 
     e.tytul AS tytul,
     CASE
         WHEN g.nazwa_galeria IS NOT NULL THEN
             'Ekspozycja: ' || g.nazwa_galeria || ', ' || ex.sala
         WHEN w.id_instytucja IS NOT NULL THEN
             'Wypozyczony: ' || w.nazwa || ', ' || w.miasto
         ELSE
             'Magazyn'
     END AS status 
 FROM
     Eksponaty e
 LEFT JOIN
     Ekspozycje ex ON e.id_eksponat = ex.id_eksponat
                   AND (ex.data_kon IS NULL OR ex.data_kon > CURRENT_DATE)
 LEFT JOIN
     Galerie g ON ex.id_galeria = g.id_galeria
 LEFT JOIN
     Wypozyczenia w ON e.id_eksponat = w.id_eksponat
                    AND (w.data_zwro IS NULL OR w.data_zwro > CURRENT_DATE)";
$result = pg_query($link, $result_query);

$numrows = pg_numrows($result);
?>

<h2 align=center>Eksponaty</h2>

<table border="1" align=center>
<tr>
 <th>ID Eksponatu</th>
 <th>Tytul</th>
 <th>Status</th>
</tr>
<?php

 for($ri = 0; $ri < $numrows; $ri++) {
  echo "<tr>\n";
  $row = pg_fetch_array($result, $ri);
  echo " <td>" . $row["id_eksponat"] . "</td>\n";
  echo " <td>" . $row["tytul"] . "</td>\n";
  echo " <td>" . $row["status"] . "</td>
 </tr>
";
 }
 pg_close($link);
?>
</table>
</body>
</html>

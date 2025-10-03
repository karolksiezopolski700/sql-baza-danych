#!/usr/bin/php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Muzeum</title>
</head>
<body>
    <h1>Muzeum</h1>
    <form action="Przekierowanie.cgi" method="GET"> 
        <label>
            <input type="radio" name="program" value="program1" checked> Przeszukiwanie eksponatow
        <br>
        <label>
            <input type="radio" name="program" value="program2"> Dodaj eksponat
        </label>
        <br>
        <label>
            <input type="radio" name="program" value="program3"> Dodaj galerię
        </label>
        <br>
        <label>
            <input type="radio" name="program" value="program4"> Zmien informacje o polozeniu eksponatu
        </label>
        <br>
        <label>
            <input type="radio" name="program" value="program5"> Zmien okres trwania ekspozycji
        </label>
        <br>
        <label>
            <input type="radio" name="program" value="program6"> Zmien okres trwania wypozyczenia
        </label>
        <br>
        <button type="submit">Wybierz</button>
    </form>
</body>
</html>

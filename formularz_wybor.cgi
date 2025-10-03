#!/usr/bin/php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Wybierz</title>
</head>
<body>
    <form action="Przekierowanie2.cgi" method="GET"> 
        <p>Pracownik muzeum: <input type="radio" name="wybor" value="pracownik" checked></p>
        <p>Zwiedzajacy: <input type="radio" name="wybor" value="zwiedzajacy"></p>

        <input type="submit" value="Wybierz">
    </form>
</body>
</html>

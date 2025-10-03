#!/usr/bin/php
<?php
echo("Content-type: text/html\n\n");
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Logowanie</title>
</head>
<body>
    <h1>Logowanie</h1>
    <form action="login.cgi" method="GET"> 
        <p>Login: <input type="text" name="username" required></p>
        <p>Haslo: <input type="password" name="password" required></p>

        <input type="submit" value="Zaloguj sie">
    </form>
</body>
</html>

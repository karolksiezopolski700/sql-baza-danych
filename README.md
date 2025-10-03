# System obsługi eksponatów muzealnych (projekt studencki)

## Opis projektu
Projekt miał na celu wspomaganie muzeum sztuki w zarządzaniu eksponatami (obrazami, rzeźbami itp.) poprzez komputerową bazę danych i prostą aplikację internetową.  
Umożliwia przechowywanie informacji o dziełach sztuki, ich twórcach, galeriach oraz wypożyczeniach do innych instytucji.

## Co zrobiłem
- Stworzyłem bazę danych w PostgreSQL, zawierającą informacje o:
  - eksponatach (unikalny kod, tytuł, typ, wymiary i wagę),  
  - artystach (ID, imię, nazwisko, rok urodzenia i rok śmierci),  
  - galeriach muzeum,  
  - historii położenia eksponatów i wypożyczeń.  
- Zaimplementowałem prostą stronę internetową (HTML/CSS/PHP), która umożliwia:
  - wprowadzanie nowych eksponatów, artystów i galerii,  
  - aktualizację położenia eksponatów,  
  - wprowadzanie i przeglądanie wypożyczeń,  
  - wyszukiwanie dzieł danego artysty oraz informacji o dostępności dla zwiedzających.  
- Przygotowałem diagram bazy danych pokazujący tabele i połączenia między nimi.  

## Zasady, które zostały uwzględnione
- Żaden eksponat nie może przebywać poza muzeum dłużej niż 30 dni rocznie.  
- Muzeum zawsze posiada przynajmniej jeden eksponat każdego artysty w swoich galeriach lub magazynie.  
- Historia ekspozycji i wypożyczeń jest przechowywana, nie tylko aktualne położenie eksponatów.  

## Jak uruchomić projekt lokalnie
1. Zainstaluj PostgreSQL na swoim komputerze (np. przez PgAdmin).  
2. Utwórz nową bazę danych i zaimportuj plik `schema.sql` (tworzy tabele i przykładowe dane).  
3. W plikach PHP zmień dane połączenia z bazy danych na lokalne:
   ```php
   $link = pg_connect("host=localhost dbname=twoja_baza user=twoj_user password=twoje_haslo");

drop table if exists Wypozyczenia;
drop table if exists Ekspozycje;
drop table if exists Eksponaty;
drop table if exists Artysci;
drop table if exists Galerie;
drop view if exists LiczbaDniNaWypo;
drop view if exists Stan_eksp;

CREATE TABLE Galerie (
    id_galeria VARCHAR(5) PRIMARY KEY,
    nazwa_galeria VARCHAR(30) NOT NULL
);

CREATE TABLE Artysci (
    id_artysta VARCHAR(5) PRIMARY KEY,
    imie VARCHAR(15) NOT NULL,
    nazwisko VARCHAR(30) NOT NULL,
    rok_urodzenia INT NOT NULL,
    rok_smierci INT
);

CREATE TABLE Eksponaty (
    id_eksponat VARCHAR(5) PRIMARY KEY,
    tytul VARCHAR(40) NOT NULL,
    typ VARCHAR(20) NOT NULL,
    wysokosc INT NOT NULL,
    szerokosc INT NOT NULL,
    waga INT NOT NULL,
    id_artysta VARCHAR(5) REFERENCES Artysci(id_artysta),
    do_wypozyczenia VARCHAR(3) NOT NULL
);

CREATE TABLE Ekspozycje (
    id_ekspozycja VARCHAR(5) PRIMARY KEY,
    id_eksponat VARCHAR(5) REFERENCES Eksponaty(id_eksponat),
    id_galeria VARCHAR(5) REFERENCES Galerie(id_galeria),
    sala VARCHAR(10) NOT NULL,
    data_pocz DATE NOT NULL,
    data_kon DATE
);

CREATE TABLE Wypozyczenia (
    id_wypozyczenie VARCHAR(5) PRIMARY KEY,
    id_eksponat VARCHAR(5) REFERENCES Eksponaty(id_eksponat),
    id_instytucja VARCHAR(5) NOT NULL,
    nazwa VARCHAR(30) NOT NULL,
    miasto VARCHAR(25) NOT NULL,
    data_wypo DATE NOT NULL,
    data_zwro DATE NOT NULL
);


-- Usuwanie artysty ktorego dziel nie ma w muzeum
CREATE OR REPLACE FUNCTION UsunArtyste()
RETURNS TRIGGER AS $$
BEGIN
	DELETE FROM Artysci WHERE id_artysta = OLD.id_artysta 
	AND NOT EXISTS (SELECT 1 FROM Eksponaty WHERE id_artysta = OLD.id_artysta);
	RETURN NULL;
END;
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE TRIGGER UsunPoUsunieciuEksponatu
AFTER DELETE ON Eksponaty
FOR EACH ROW
EXECUTE PROCEDURE UsunArtyste();

-- Sprawdzanie czy dodany artysta ma rok smierci wiekszy rowny od roku urodzenia
CREATE OR REPLACE FUNCTION sprawdz_rok_smierci()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.rok_smierci IS NOT NULL AND NEW.rok_smierci < NEW.rok_urodzenia THEN
        RAISE EXCEPTION 'Rok smierci nie moze byc mniejszy od roku urodzenia!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER sprawdz_rok_smierci_insert
BEFORE INSERT ON Artysci
FOR EACH ROW
EXECUTE PROCEDURE sprawdz_rok_smierci();

-- Sprawdzanie czy dodana ekspozycja ma date konca wieksza rowna od roku zakonczenia
CREATE OR REPLACE FUNCTION sprawdz_data_ekspozycji()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.data_kon IS NOT NULL AND NEW.data_kon < NEW.data_pocz THEN
        RAISE EXCEPTION 'Data poczatku ekspozycji nie moze byc mniejsza od daty zakonczenia ekspozycji!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER sprawdz_data_ekspozycji_insert
BEFORE INSERT ON Ekspozycje
FOR EACH ROW
EXECUTE PROCEDURE sprawdz_data_ekspozycji();

-- Sprawdzanie czy dodane wypozycznie ma date konca wieksza rowna od roku zakonczenia
CREATE OR REPLACE FUNCTION sprawdz_data_wypo()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.data_zwro IS NOT NULL AND NEW.data_zwro < NEW.data_wypo THEN
        RAISE EXCEPTION 'Data poczatku ekspozycji nie moze byc mniejsza od daty zakonczenia ekspozycji!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER sprawdz_data_wypo_insert
BEFORE INSERT ON Wypozyczenia
FOR EACH ROW
EXECUTE PROCEDURE sprawdz_data_wypo();


CREATE OR REPLACE FUNCTION sprawdz_nachodzenie_ekspozycji()
RETURNS TRIGGER AS $$
BEGIN
    -- Sprawdzenie, czy eksponat nie jest już na ekspozycji w nakładającym się okresie
    IF EXISTS (
        SELECT 1
        FROM Ekspozycje
        WHERE id_eksponat = NEW.id_eksponat AND id_ekspozycja != NEW.id_ekspozycja
        AND (
            (NEW.data_pocz BETWEEN data_pocz AND COALESCE(data_kon, NEW.data_pocz)) OR
            (NEW.data_kon IS NOT NULL AND NEW.data_kon BETWEEN data_pocz AND COALESCE(data_kon, NEW.data_kon)) OR
            (data_pocz BETWEEN NEW.data_pocz AND COALESCE(NEW.data_kon, data_pocz))
        )
    ) THEN
        RAISE EXCEPTION 'Eksponat jest już na innej ekspozycji w tym okresie!';
    END IF;

    -- Sprawdzenie, czy eksponat nie jest wypożyczony w tym okresie
    IF EXISTS (
        SELECT 1
        FROM Wypozyczenia
        WHERE id_eksponat = NEW.id_eksponat
        AND (
            (NEW.data_pocz BETWEEN data_wypo AND COALESCE(data_zwro, NEW.data_pocz)) OR
            (NEW.data_kon IS NOT NULL AND NEW.data_kon BETWEEN data_wypo AND COALESCE(data_zwro, NEW.data_kon)) OR
            (data_wypo BETWEEN NEW.data_pocz AND COALESCE(NEW.data_kon, data_wypo))
        )
    ) THEN
        RAISE EXCEPTION 'Eksponat jest już wypożyczony w tym okresie!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER sprawdz_nachodzenie_ekspozycji_insert
BEFORE INSERT OR UPDATE ON Ekspozycje
FOR EACH ROW
EXECUTE PROCEDURE sprawdz_nachodzenie_ekspozycji();


CREATE OR REPLACE FUNCTION sprawdz_nachodzenie_wypo()
RETURNS TRIGGER AS $$
BEGIN
    -- Sprawdzenie, czy eksponat nie jest wypożyczony w nakładającym się okresie
    IF EXISTS (
        SELECT 1
        FROM Wypozyczenia
        WHERE id_eksponat = NEW.id_eksponat AND id_wypozyczenie != NEW.id_wypozyczenie
        AND (
            (NEW.data_wypo BETWEEN data_wypo AND COALESCE(data_zwro, NEW.data_wypo)) OR
            (NEW.data_zwro IS NOT NULL AND NEW.data_zwro BETWEEN data_wypo AND COALESCE(data_zwro, NEW.data_zwro)) OR
            (data_wypo BETWEEN NEW.data_wypo AND COALESCE(NEW.data_zwro, data_wypo))
        )
    ) THEN
        RAISE EXCEPTION 'Eksponat jest już wypożyczony w tym okresie!';
    END IF;

    -- Sprawdzenie, czy eksponat nie jest na ekspozycji w tym okresie
    IF EXISTS (
        SELECT 1
        FROM Ekspozycje
        WHERE id_eksponat = NEW.id_eksponat
        AND (
            (NEW.data_wypo BETWEEN data_pocz AND COALESCE(data_kon, NEW.data_wypo)) OR
            (NEW.data_zwro IS NOT NULL AND NEW.data_zwro BETWEEN data_pocz AND COALESCE(data_kon, NEW.data_zwro)) OR
            (data_pocz BETWEEN NEW.data_wypo AND COALESCE(NEW.data_zwro, data_pocz))
        )
    ) THEN
        RAISE EXCEPTION 'Eksponat jest już na ekspozycji w tym okresie!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER sprawdz_nachodzenie_wypo_insert
BEFORE INSERT OR UPDATE ON Wypozyczenia
FOR EACH ROW
EXECUTE PROCEDURE sprawdz_nachodzenie_wypo();

-- Zmiana wartosci do wypo na "nie" 
CREATE OR REPLACE FUNCTION zmien_do_wypozyczenia_na_nie_exp()
RETURNS TRIGGER AS $$

DECLARE
ile INT;
ile_wypo INT;
art VARCHAR(5);

BEGIN
    IF NEW.data_pocz <= CURRENT_DATE AND (NEW.data_kon IS NULL OR CURRENT_DATE < NEW.data_kon) THEN
        UPDATE Eksponaty
        SET do_wypozyczenia = 'nie'
        WHERE id_eksponat = NEW.id_eksponat;
    END IF;
    IF NEW.data_kon = CURRENT_DATE THEN
				EXECUTE format('CREATE OR REPLACE VIEW Stan_eksp AS
				SELECT
						 e.id_eksponat AS id_eksponat, 
					 e.tytul AS tytul,
					 CASE
						 WHEN g.nazwa_galeria IS NOT NULL THEN
							 ''E''
						 WHEN w.id_instytucja IS NOT NULL THEN
							 ''W''
						 ELSE
							 ''M''
					 END AS stat, a.id_artysta AS id_artysta 
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
				LEFT JOIN Artysci a ON e.id_artysta = a.id_artysta');
		SELECT id_artysta INTO art FROM Eksponaty WHERE id_eksponat = NEW.id_eksponat;
		SELECT COUNT(*) INTO ile FROM Eksponaty WHERE id_artysta = art;
		SELECT COUNT(*) INTO ile_wypo FROM Stan_eksp S JOIN Eksponaty E ON S.id_eksponat = E.id_eksponat WHERE E.id_artysta = art AND S.stat = 'W';
		IF ile - ile_wypo >= 2 THEN
			UPDATE Eksponaty
			SET do_wypozyczenia = 'tak' 
			WHERE id_eksponat IN (SELECT E.id_eksponat FROM Eksponaty E JOIN Stan_eksp S ON E.id_eksponat = S.id_eksponat WHERE S.stat = 'M');
		END IF;
	END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER zmien_do_wypozyczenia_insert_or_update_exp
AFTER INSERT OR UPDATE ON Ekspozycje
FOR EACH ROW
EXECUTE PROCEDURE zmien_do_wypozyczenia_na_nie_exp();


CREATE OR REPLACE FUNCTION zmien_do_wypozyczenia_na_nie_wypo()
RETURNS TRIGGER AS $$
DECLARE
	ile INT;
	ile_wypo INT;
	art VARCHAR(5);
BEGIN
    IF NEW.data_wypo <= CURRENT_DATE AND (NEW.data_zwro IS NULL OR CURRENT_DATE < NEW.data_zwro) THEN
        UPDATE Eksponaty
        SET do_wypozyczenia = 'nie'
        WHERE id_eksponat = NEW.id_eksponat;
    END IF;
    IF NEW.data_zwro = CURRENT_DATE THEN
				EXECUTE format('CREATE OR REPLACE VIEW Stan_eksp AS
				SELECT
						 e.id_eksponat AS id_eksponat, 
					 e.tytul AS tytul,
					 CASE
						 WHEN g.nazwa_galeria IS NOT NULL THEN
							 ''E''
						 WHEN w.id_instytucja IS NOT NULL THEN
							 ''W''
						 ELSE
							 ''M''
					 END AS stat, a.id_artysta AS id_artysta 
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
				LEFT JOIN Artysci a ON e.id_artysta = a.id_artysta');
		SELECT id_artysta INTO art FROM Eksponaty WHERE id_eksponat = NEW.id_eksponat;
		SELECT COUNT(*) INTO ile FROM Eksponaty WHERE id_artysta = art;
		SELECT COUNT(*) INTO ile_wypo FROM Stan_eksp S JOIN Eksponaty E ON S.id_eksponat = E.id_eksponat WHERE E.id_artysta = art AND S.stat = 'W';
		IF ile - ile_wypo >= 2 THEN
			UPDATE Eksponaty
			SET do_wypozyczenia = 'tak' 
			WHERE id_eksponat IN (SELECT E.id_eksponat FROM Eksponaty E JOIN Stan_eksp S ON E.id_eksponat = S.id_eksponat WHERE S.stat = 'M');
		END IF;
	END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER zmien_do_wypozyczenia_insert_or_update_wypo
AFTER INSERT OR UPDATE ON Wypozyczenia
FOR EACH ROW
EXECUTE PROCEDURE zmien_do_wypozyczenia_na_nie_wypo();

CREATE OR REPLACE FUNCTION czy_przekracza_30_dni()
RETURNS TRIGGER AS $$

DECLARE
pom INT; 
pom1 INT; 
pom2 INT;

BEGIN
	EXECUTE format('CREATE OR REPLACE VIEW LiczbaDniNaWypo AS
					SELECT
					id_eksponat,
					EXTRACT(YEAR FROM data_wypo) AS rok,
					SUM(
						GREATEST(
							LEAST(data_zwro, make_date(EXTRACT(YEAR FROM data_wypo)::INT, 12, 31)) -
							GREATEST(data_wypo, make_date(EXTRACT(YEAR FROM data_wypo)::INT, 1, 1)),
							0
						)
					) AS liczba_dni
					FROM
						Wypozyczenia
					GROUP BY
						id_eksponat,
						EXTRACT(YEAR FROM data_wypo)'); 
	IF EXTRACT(YEAR FROM NEW.data_wypo) = EXTRACT(YEAR FROM NEW.data_zwro) THEN
		SELECT liczba_dni INTO pom FROM LiczbaDniNaWypo WHERE rok = EXTRACT(YEAR FROM NEW.data_wypo) AND id_eksponat = NEW.id_eksponat;
		IF COALESCE(pom,0)>30 THEN
			RAISE EXCEPTION '1 IF, dni %',(COALESCE(pom,0) + dni);
		END IF;
	ELSIF EXTRACT(YEAR FROM NEW.data_wypo) + 1 < EXTRACT(YEAR FROM NEW.data_zwro) THEN
		RAISE EXCEPTION '2 IF';
	ELSIF EXTRACT(YEAR FROM NEW.data_wypo) + 1 = EXTRACT(YEAR FROM NEW.data_zwro) THEN
		SELECT liczba_dni INTO pom1 FROM LiczbaDniNaWypo WHERE rok = EXTRACT(YEAR FROM NEW.data_wypo) AND id_eksponat = NEW.id_eksponat;
		SELECT liczba_dni INTO pom2 FROM LiczbaDniNaWypo WHERE rok = EXTRACT(YEAR FROM NEW.data_zwro) AND id_eksponat = NEW.id_eksponat;
		IF COALESCE(pom1,0) >30 OR COALESCE(pom2,0) >30 THEN
			RAISE EXCEPTION '3 IF';
		END IF;
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER czy_przekracza_30_dni_insert
AFTER INSERT OR UPDATE ON Wypozyczenia
FOR EACH ROW
EXECUTE PROCEDURE czy_przekracza_30_dni();			

-- Czy do wypozyczenia 30 dni
CREATE OR REPLACE FUNCTION czy_przekracza_30_dni_zmien_do_wypo()
RETURNS TRIGGER AS $$

DECLARE
pom INT; 

BEGIN
	EXECUTE format('CREATE OR REPLACE VIEW LiczbaDniNaWypo AS
					SELECT
					id_eksponat,
					EXTRACT(YEAR FROM data_wypo) AS rok,
					SUM(
						GREATEST(
							LEAST(data_zwro, make_date(EXTRACT(YEAR FROM data_wypo)::INT, 12, 31)) -
							GREATEST(data_wypo, make_date(EXTRACT(YEAR FROM data_wypo)::INT, 1, 1)),
							0
						)
					) AS liczba_dni
					FROM
						Wypozyczenia
					GROUP BY
						id_eksponat,
						EXTRACT(YEAR FROM data_wypo)'); 

	SELECT liczba_dni INTO pom FROM LiczbaDniNaWypo WHERE rok = EXTRACT(YEAR FROM NEW.data_wypo) AND id_eksponat = NEW.id_eksponat;
	IF COALESCE(pom,0)=30 AND EXTRACT(YEAR FROM CURRENT_DATE) = EXTRACT(YEAR FROM NEW.data_wypo)THEN
		UPDATE Eksponaty
		SET do_wypozyczenia = 'nie'
		WHERE id_eksponat = NEW.id_eksponat;

	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER czy_przekracza_30_dni_zmien_do_wypo_insert
AFTER INSERT OR UPDATE ON Wypozyczenia
FOR EACH ROW
EXECUTE PROCEDURE czy_przekracza_30_dni_zmien_do_wypo();

CREATE OR REPLACE FUNCTION czy_mozna_wypo()
RETURNS TRIGGER AS $$
DECLARE
war VARCHAR(3);
BEGIN
	SELECT do_wypozyczenia INTO war FROM Eksponaty WHERE id_eksponat = NEW.id_eksponat;
	IF war = 'nie' THEN
		RAISE EXCEPTION 'Nie do wypozyczenia';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER czy_mozna_wypo_insert
BEFORE INSERT ON Wypozyczenia
FOR EACH ROW
EXECUTE PROCEDURE czy_mozna_wypo();


CREATE OR REPLACE FUNCTION zmien_status()
RETURNS TRIGGER AS $$
DECLARE
	art VARCHAR(5);
	ile INT;
	ile_wypo INT;
BEGIN
	EXECUTE format('CREATE OR REPLACE VIEW Stan_eksp AS
					SELECT
							 e.id_eksponat AS id_eksponat, 
						 e.tytul AS tytul,
						 CASE
							 WHEN g.nazwa_galeria IS NOT NULL THEN
								 ''E''
							 WHEN w.id_instytucja IS NOT NULL THEN
								 ''W''
							 ELSE
								 ''M''
						 END AS stat, a.id_artysta AS id_artysta 
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
					LEFT JOIN Artysci a ON e.id_artysta = a.id_artysta');
	SELECT id_artysta INTO art FROM Eksponaty WHERE id_eksponat = NEW.id_eksponat;
	SELECT COUNT(*) INTO ile FROM Eksponaty WHERE id_artysta = art;
	SELECT COUNT(*) INTO ile_wypo FROM Stan_eksp S JOIN Eksponaty E ON S.id_eksponat = E.id_eksponat WHERE E.id_artysta = art AND S.stat = 'W';
	IF ile - ile_wypo <= 1 THEN
		UPDATE Eksponaty
        SET do_wypozyczenia = 'nie'
        WHERE id_artysta = art;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER zmien_status_insert
AFTER INSERT ON Wypozyczenia
FOR EACH ROW
EXECUTE PROCEDURE zmien_status();

CREATE OR REPLACE FUNCTION jaka_do_wypo()
RETURNS TRIGGER AS $$
DECLARE
	ile INT;
	ile_wypo INT;
BEGIN
	EXECUTE format('CREATE OR REPLACE VIEW Stan_eksp AS
					SELECT
							 e.id_eksponat AS id_eksponat, 
						 e.tytul AS tytul,
						 CASE
							 WHEN g.nazwa_galeria IS NOT NULL THEN
								 ''E''
							 WHEN w.id_instytucja IS NOT NULL THEN
								 ''W''
							 ELSE
								 ''M''
						 END AS stat, a.id_artysta AS id_artysta 
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
					LEFT JOIN Artysci a ON e.id_artysta = a.id_artysta');
	SELECT COUNT(*) INTO ile FROM Eksponaty WHERE id_artysta = NEW.id_artysta;
	SELECT COUNT(*) INTO ile_wypo FROM Stan_eksp S JOIN Eksponaty E ON S.id_eksponat = E.id_eksponat WHERE E.id_artysta = NEW.id_artysta AND S.stat = 'W';
	IF ile - ile_wypo <= 1 THEN
		UPDATE Eksponaty
        SET do_wypozyczenia = 'nie'
        WHERE id_artysta = NEW.id_artysta;
        ELSIF ile-ile_wypo >= 2 THEN
			UPDATE Eksponaty
			SET do_wypozyczenia = 'tak'
			WHERE id_artysta = NEW.id_artysta AND id_eksponat IN (SELECT E.id_eksponat FROM Eksponaty E JOIN Stan_eksp S ON E.id_eksponat = S.id_eksponat WHERE S.stat = 'M');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER jaka_do_wypo_insert
AFTER INSERT ON Eksponaty
FOR EACH ROW
EXECUTE PROCEDURE jaka_do_wypo();







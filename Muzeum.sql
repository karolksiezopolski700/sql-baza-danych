drop table if exists Wypozyczenia;
drop table if exists Ekspozycje;
drop table if exists Eksponaty;
drop table if exists Artysci;
drop table if exists Galerie;

CREATE TABLE Galerie (
    id_galeria VARCHAR(5) PRIMARY KEY
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
    data_zwro DATE
);



CREATE OR REPLACE FUNCTION UsunArtyste()
RETURNS TRIGGER AS $$
BEGIN
	DELETE FROM Artysci WHERE id_artysta = OLD.id_artysta 
	AND NOT EXISTS (SELECT 1 FROM Eksponaty WHERE id_artysta = OLD.id_artysta);
	RETURN NULL;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER UsunPoUsunieciuEksponatu
AFTER DELETE ON Eksponaty
FOR EACH ROW
EXECUTE PROCEDURE UsunArtyste();

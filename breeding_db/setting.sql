CREATE TABLE Pigs(
    id varchar(20),
    birthday date,
    farm varchar(20),
    breed char(3),
    dam_id varchar(20),
    dam_birthday date,
    dam_farm varchar(20),
    sire_id varchar(20),
    sire_birthday date,
    sire_farm varchar(20),
    reg_id char(6),
    gender char(10),
    chinese_name char(5),
    PRIMARY KEY (id, birthday, farm),
    FOREIGN KEY (dam_id, dam_birthday, dam_farm) REFERENCES Pigs(id, birthday, farm),
    FOREIGN KEY (sire_id, sire_birthday, sire_farm) REFERENCES Pigs(id, birthday, farm)
);

CREATE TABLE Estrus(
    id varchar(20),
    birthday date,
    farm varchar(20),
    estrus_datetime datetime,
    pregnant ENUM('Yes', 'No', 'Unknown', 'Abortion'),
    parity tinyint unsigned,
    PRIMARY KEY (id, birthday, farm, estrus_datetime),
    FOREIGN KEY (id, birthday, farm) REFERENCES Pigs(id, birthday, farm)
);

CREATE TABLE Matings(
    sow_id varchar(20),
    sow_birthday date,
    sow_farm varchar(20),
    estrus_datetime datetime,
    mating_datetime datetime,
    boar_id varchar(20),
    boar_birthday date,
    boar_farm varchar(20),
    PRIMARY KEY (sow_id, sow_birthday, sow_farm, estrus_datetime, mating_datetime),
    FOREIGN KEY (sow_id, sow_birthday, sow_farm, estrus_datetime) REFERENCES Estrus(id, birthday, farm, estrus_datetime),
    FOREIGN KEY (boar_id, boar_birthday, boar_farm) REFERENCES Pigs(id, birthday, farm)
);
drop table Weanings;
drop table Farrowings;
drop table Matings;
drop table Estrus;
drop table Pigs;

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
    reg_id char(6) UNIQUE,
    gender char(10),
    chinese_name char(5),
    litter tinyint unsigned,
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
    boar_id varchar(20) NOT NULL,
    boar_birthday date NOT NULL,
    boar_farm varchar(20) NOT NULL,
    PRIMARY KEY (sow_id, sow_birthday, sow_farm, estrus_datetime, mating_datetime),
    FOREIGN KEY (sow_id, sow_birthday, sow_farm, estrus_datetime) REFERENCES Estrus(id, birthday, farm, estrus_datetime),
    FOREIGN KEY (boar_id, boar_birthday, boar_farm) REFERENCES Pigs(id, birthday, farm)
);

CREATE TABLE Farrowings(
    id varchar(20),
    birthday date,
    farm varchar(20),
    estrus_datetime datetime,
    farrowing_date date NOT NULL,
    crushed tinyint unsigned,
    black tinyint unsigned,
    weak tinyint unsigned,
    malformation tinyint unsigned,
    dead tinyint unsigned,
    total_weight float unsigned,
    n_of_male tinyint unsigned,
    n_of_female tinyint unsigned, 
    note varchar(20),
    PRIMARY KEY (id, birthday, farm, estrus_datetime, farrowing_date),
    FOREIGN KEY (id, birthday, farm, estrus_datetime) REFERENCES Estrus (id, birthday, farm, estrus_datetime)
);

CREATE TABLE Weanings(
    id varchar(20),
    birthday date,
    farm varchar(20),
    estrus_datetime datetime,
    farrowing_date date,
    weaning_date date NOT NULL,
    total_nursed_piglets tinyint unsigned, 
    total_weaning_piglets tinyint unsigned, 
    total_weaning_weight float unsigned,
    PRIMARY KEY (id, birthday, farm, estrus_datetime, farrowing_date),
    FOREIGN KEY (id, birthday, farm, estrus_datetime, farrowing_date) REFERENCES Farrowings (id, birthday, farm, estrus_datetime, farrowing_date)
);
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
    naif_id char(6),
    gender char(10),
    chinese_name char(5),
    PRIMARY KEY (id, birthday, farm),
    FOREIGN KEY (dam_id, dam_birthday, dam_farm) REFERENCES Pigs(id, birthday, farm),
    FOREIGN KEY (sire_id, sire_birthday, sire_farm) REFERENCES Pigs(id, birthday, farm)
)
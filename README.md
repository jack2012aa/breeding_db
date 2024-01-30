# Breeding-DB

## Introduction

實驗室育種組搜集了東盈、政鋼、劉銘宏三家種豬場的繁殖資料。原始資料都是excel格式，三場格式不統一且都有多個版本。這個資料庫主要目標為整理研究用資料，次要目標為發展成豬場管理系統。

ECL lab collects reproduction data from Dong-Ying, Chen-Gang and Liu farms. Data is written in Excel. Each farm has their own format and mulitple versions. The primary goal of this project is to standardize data for experiments. The secondary goal is to develop an ERP system for breeding pigs.

## ER Diagram and Input Data Relationship
![image](https://github.com/jack2012aa/breeding_db/blob/master/drawings/ER.jpg)\
Please read [here](https://github.com/jack2012aa/breeding_db/tree/master/models) for details.\
![image](https://github.com/jack2012aa/breeding_db/blob/master/drawings/CSVtoDB.jpg)

## Structure

* `data_structures`: basic structures that represent entities of a table in the database.
    * `pig`: the structure that holds the basic information of a pig.
    * `estrus`: the structure that holds the information of a single estrus.
* `factory`: classes that produce an instance of `data_structure` based on data from different farms.
* `general`: some frequently used functions.
* `models`: operations related to reading or changing the database.
* `reader`: classes that read excels to database.

## To Do
* When inserting a new pig, check birthday delta of it and last pig with the same id.
    * Possibly it is a historical data?
    * Discuss with professor Lin.
* Put 60th_day_test in Dong-Ying data into consideration.
* Ask professor Wu that should parity grow one after an abortion.
* Read total_weight as sum up of multiple weights.
* Ask <> tag in mating tables of Dong-Ying.
* Ask use choose correct sow and boar when reading estrus, mating, farrowing data.
* Discuss with professor Lin about delta ranges.

## Log

### 2024-01-30
* 

### 2024-01-29
* Transform any id into 6 digits with leading 0.
* Divide dong_ying_reader into several files.
* Restructur `DongYingPigReader`:
    * Divide into 5 steps: 1. check null, 2. set values, 3. class specific check, 4. check flags, 5. insert
    * check null now can be done by standardized method.
* Restructur `DongYingEstrusAndMatingReader`:
    * Remove auto repair.
    * Add parity check.
    * Remove part of time delta check.
* Change the default estrus time of Dong-Ying to 16:00.
* When reading estrus, if parity become smaller or parity is the same but delta > 50, then throw an error.
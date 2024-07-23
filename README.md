# Breeding-DB

## Introduction

實驗室育種組搜集了東盈、政鋼、劉銘宏三家種豬場的繁殖資料。原始資料都是excel格式，三場格式不統一且都有多個版本。這個資料庫主要目標為整理研究用資料，次要目標為發展成豬場管理系統。

ECL lab collects reproduction data from Dong-Ying, Chen-Gang and Liu farms. Data is written in Excel. Each farm has their own format and mulitple versions. The primary goal of this project is to standardize data for experiments. The secondary goal is to develop an ERP system for breeding pigs.

## Structure

* `data_structures`: basic structures that represent entities of a table in the database.
* `models`: operations related to reading or changing the database.
* `reader`: classes that read excels to database.
* `transformer`: transform excel from different farms to the standard form.
# Breeding-DB

## Introduction

實驗室育種組搜集了東盈、政鋼、劉銘宏三家種豬場的繁殖資料。原始資料都是excel格式，三場格式不統一且都有多個版本。這個資料庫主要目標為整理研究用資料，次要目標為發展成豬場管理系統。

ECL lab collects reproduction data from Dong-Ying, Chen-Gang and Liu farms. Data is written in Excel. Each farm has their own format and mulitple versions. The primary goal of this project is to standardize data for experiments. The secondary goal is to develop an ERP system for breeding pigs.

## Structure

* `data_structures`: basic structures that represent entities of a table in the database.
* `models`: operations related to reading or changing the database.
* `reader`: classes that read excels to database.
* `transformer`: transform excel from different farms to the standard form.

## 使用方法

1. 下載app.exe
2. 建立一個專門的文件夾放置 app.exe
3. 在文件夾中新增 database_settings.json，設定如何連接到資料庫
4. 資料庫使用 mysql，會安裝在實驗室大電腦
5. 一定要注意不要把 database_settings.json 上傳到任何雲端
6. 在文件夾中再新增一個文件夾，專門放輸出資料
7. 只有在實驗室的網路內可以連接上資料庫
8. 打開程式後後首先選擇是要轉換資料表或是讀取資料
9. 選擇牧場
10. 輸入檔案位置，不確定位置的話可以在檔案總管中找到該檔案並對它按右鍵，選擇"內容"並複製"位置"
11. 輸出檔案位置輸入步驟4建立的文件夾名稱或是其他
12. 如果是讀取資料，選擇要讀取的種類以及是否允許空值

## 抓取資料
可以使用 python 中的 pandas 和 pymysql，可參閱[這篇文章](https://blog.csdn.net/The_Time_Runner/article/details/86601988)。

### 範例
```python
# Import 前記得透過 pip 安裝
import pymysql
import pandas as pd

connection = pymysql.connect(host=host, user=username, password=password, database=database_name, charset="utf-8")

# query 就是接下來要講的 SQL 搜尋語句.
query = "..."
dataframe = pd.read_sql(query, connection)
dataframe.to_excel("output_path", "sheet_name")
```

### 搜尋的基本語法：
```sql
SELECT attribute_1, attribute_2, ...
FROM table_name
WHERE attribute_3=..., attribute_4...
ORDER BY attribute_5 ASC;
```
其中`SELECT`後面接的是想要輸出的屬性，除了 table 中定義的屬性外，也可以使用 SUM(), COUNT(), CONCAT() 等函式幫忙把屬性變成自己想要的模樣。

`FROM`後面接的是想要搜尋的table。

`WHERE`是搜尋的條件，包含`=`, `>`, `>=`, `<`, `<=`, `!=` 等等。

`ORDER BY` 可以依照想要的屬性排列輸出，`ASC` 是升序，`DESC`是降序。

後兩者可以不寫。

### 函式的使用
例如如果想要輸出正綱的系譜，並且全部以`出生年+耳號`作為編號的話，那就可以使用 CONCAT() 把多個文字屬性連在一起，並用 YEAR() 提取年份：
```sql
SELECT CONCAT(YEAR(birthday), id) AS pig_id, CONCAT(YEAR(sire_birthday), sire_id) AS sire_id, CONCAT(YEAR(dam_birthday), dam_id) AS dam_id 
FROM Pigs 
WHERE farm='Chen-Gang';
```

### Foreign keys 與 Join
Foreign keys 是指某個屬性的值必須是在指定 table 中實際出現過的值。例如 `Pigs` 中的 `sire_id`, `sire_farm`, `sire_birthday`就是一個 foreign key，它對應到 `Pigs` 中的 `id`, `farm`, `birthday`。也就是說，我想指定一頭豬的父畜時，父畜本身需要存在於 `Pigs` 中。

Foreign key 是保證關連式資料庫 relational database 資料正確的重要特性。更詳細的可以看網路上的講解，這邊不贅述。

有些值需要透過 foreign key 搜尋。例如如果我想知道某頭豬父畜的品種，雖然可以先查到父畜的 primary key，也就是 sire_id, sire_farm, sire_birthday，之後再進行查詢，但其實有更好的方式，也就是使用 `JOIN`。`JOIN`的作用是把兩張表透過 foreign key 合併成一張臨時的表，這張表會被 `FROM` 語句使用。

為了更好的體現 JOIN 的萬能之處，假設我們現在要輸出正綱所有分娩+離乳資料的活仔數（分娩資料），哺乳數與離乳數（離乳資料）：
```sql
SELECT 
CONCAT(YEAR(Farrowings.birthday), Farrowings.id) AS sow_id, SUM(Farrowings.n_of_male, Farrowings.n_of_female) AS born_alive, 
Weanings.total_nursed_piglets, 
Weanings.total_weaning_piglets
FROM Farrowings 
INNER JOIN Weanings 
    ON Farrowings.id = Weanings.id AND Farrowings.birthday = Weanings.birthday AND Farrowings.farm = Weanings.farm AND Farrowings.estrus_datetime = Weanings.estrus_datetime
WHERE Farrowings.farm='Chen-Gang';
```
因為 `JOIN` 的表格中可能含有重複的屬性名稱，因此在選擇屬性時最好使用 `table.attribute` 指定屬性。

`ON` 定義了我們要用什麼條件 `JOIN` 兩張表格，這裏指定了 id, birthday, farm, estrus_datetime 全部都要相同。

這個 query 回傳的將會是：
1. 所有正綱母豬
2. 每一筆有對應離乳資料的分娩資料
3. 的分娩活仔數、哺乳數以及離乳數

### 不同種類的 JOIN
`JOIN` 有許多不同的種類，例如剛才的範例用到的是 `INNER JOIN`，是只有當 `ON` 後面的條件都符合時才會讓資料輸出的方法。例如如果有一筆分娩資料並沒有對應的離乳資料，則因為條件不符合所以不會被放到輸出中。

如果想要無視有沒有離乳資料，硬輸出所有分娩資料的話，要使用的就是 `LEFT JOIN`。

強烈建議閱讀[這份筆記](https://medium.com/jimmy-wang/sql-%E5%B8%B8%E7%94%A8%E8%AA%9E%E6%B3%95%E5%BD%99%E6%95%B4-%E5%9F%BA%E6%9C%AC%E9%81%8B%E7%AE%97-sql-003-3b771d4dacb8)，裡面詳細說明了不同種 JOIN 的差別。

### JOIN 多個 tables
同一句 sql 語句中可以含有多個 `JOIN`。例如如果今天要輸出的系譜資料是以`出生年+品種＋耳號`作為編號，因爲父母畜的品種需要回頭查閱 `Pigs` 表格，因此需要針對父畜和母畜各 JOIN 一次。
```sql
SELECT CONCAT(YEAR(Pigs.birthday), Pigs.breed, Pigs.id) AS pig_id, 
    CONCAT(YEAR(Dam.birthday), Dam.breed, Dam.id) AS dam_id, 
    CONCAT(YEAR(Sire.birthday), Sire.breed, Sire.id) AS sire_id 
FROM Pigs 
INNER JOIN Pigs AS Sire
    ON Pigs.sire_id = Sire.id AND Pigs.sire_farm = Sire.farm AND Pigs.sire_birthday = Sire.birthday 
INNER JOIN Pigs AS Dam 
    ON Pigs.dam_id = Dam.id AND Pigs.dam_farm = Dam.farm AND Pigs.dam_birthday = Dam.birthday
WHERE Pigs.farm='Dong-Ying';
```
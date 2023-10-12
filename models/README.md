# Database Design
## ER Diagram
![image]()

## Tables
### Pigs
This table lists basic information of pigs, such as pedigree and ID.

Each farm has their own rules on giving ID to pigs. A common way is given an increasing 4-digit number represents the number of pigs in the farm, a dash, and then an 2-digit number represents the number of pigs in its parity. For example, 1902-02 means that it is the 1902th pig in the farm and 2nd pig of its siblings. Duplicated ID may appears every few years. `ID` + `birthday` is clear for a single farm, but different farm may have pigs with same `ID` and `birthday` in a very little opportunity. Hence, `ID`, `birthday` and `farm` as the key value works better.

As mentioned, `ID` is hard to be standardized. I suppose that most farms use the __xxxx-yy__ naming system and let __xxxxyy__ be our standardized `ID` (partially due to the requirement from lab members).

Farms do not have independent data sheet for individual pigs in general. However, listing individuals allows us to keep tracks on their reproduction performances, ex. knowing the total production during lifetime of a sow. Hence the correctness of this table is essential for this database. 

> Developer note: If we want to develop this database to an ERP system, a `original_id` field is necessary. It allows farms to remain there naming system.

### Estrus/Parity
This table lists estrus of sows. Every reproduction events must belong to an estrus. For instance, a sow will not mate without an estrus.

In reality, farms __will__ mate the sows whenever sows are having estrus. They commonly mate the sows two to three times in an estrus. Hence the result of mating, or, whether the sow getting `pregnant`, is better logged here, in contrast with logged in `Matings`.

``
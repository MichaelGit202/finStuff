"section 14, Intro to kdb+"
/table ex
([] s:`a`b`c; v:100 200 300)

/schema
([] s:`symbol$(); v:`int$())


meta ([] s:`symbol$(); v:`int$())


/ foreign key 
kt:([id:1001 1002 1003] s:`a`b`c; v:100 200 300)
t:([]; id:`kt$1002 1001 1003 1001; q:100 101 102 103)
meta t

/ foregin keyu access with the dot operator
select id.v, q from t


/ Here is the previous foreign-key example redone with a link column against a table.
"another fk example"
tk:([] id:1001 1002 100; s:`a`b`c; v:100 200 300)
t:([]; id:`tk!(exec id from tk)?1002 1001 1003 1001; q:100 101 102 103)
meta t

"saving foreign key tables"
`:data/kt set kt
`:data/tk set tk   
`:data/t1 set ([]; id:`kt$1002 1001 1003 1001; q:100 101 102 103)
`:data/t2 set ([]; id:`kt!(exec id from tk)?1002 1001 1003 1001; q:100 101 102 103)


kt:get `:data/kt
tk:get `:data/tk
t1:get `:data/t1
t2:get `:data/t2

"you can query by file location"
`:data/t set ([] s:`a`b`c; v:100 200 300)
select from `:data/t where s in `a`c

select from `:data/t where s in `a`c

/upsert means if record exists update it otherwise insert it
`:data/t upsert (`x;42)

/keyed table
`:data/kt set ([k:`a`b`c] v:10 20 30)
`:data/kt upsert (`b;200)
`:data/kt upsert (`x;42)
select from `:data/kt

"splayed table example"
`:data/st/ set ([] v1:10 20 30; v2:1.1 2.2 3.3)
/upsert even creates files if they don't exist
/`:data/st2/ upsert ([] v1:10 20 30; v2:1.1 2.2 3.3)

get `:data/st/v1
get `:data/st/v2

"keyed tables cannot be splayed"

"partitioned tables"
/ for columns that are too damn long
/example is slicing daily price data for a stock by dat
/
 root
     partitionvalue1
        tablename
            .d
            column1name
            column2name
            …
    partitionvalue2
        tablename
            .d
            column1name
            column2name
            …
        …


Since a partition directory name factors out the common value for all records in its slice, do not include the partition
column when you splay a partition slice – e.g., do not include a date column for a daily partitioned table. Instead, kdb+ 
infers the name, value and type from the partition directory name and creates a virtual column from this information. The 
name of the virtual column is set by q and cannot be controlled.

basically dont have "march 28th 2026" entry for every column, just have a directory named "2026.03.28" and kdb+ will create a virtual column with the date for you
(so like partition value1 would be "2026.03.28" and the virtual column would be named "date" and have the value "2026.03.28" for every record in that partition)
\

`:data/db/2015.01.01/t/ set ([] ti:09:30:00 09:31:00; p:101 102f)
`:data/db/2015.01.02/t/ set ([] ti:09:30:00 09:31:00; p:101.5 102.5)

\l data/db

t

count t
cols t
type t
meta t

/ does not work on partitioned tables because they have virtual columns
/ 
t[0j]
t[;`p]
0#t
exec from t
select[1] from t
`p xasc t
\

/work around for partitioned tables
/exec … from select … from … 


select from t where date=first date / first date
select from t where date=max date / last date

"Always place the partition column constraint first."
select from t where date=2015.01.01, ti<09:30:30

/virtual column i does not refer to absolute row number as it does with in-memory and splayed tables. Instead, it refers to the relative row number within a partition.
select from t where date=first date, i=0
select from t where date=max date, i=max i


/ you can arbitratilly specify the partition by just a number if you want
/`:/db/1/t/ set ([] ti:09:30:00 09:31:00; p:101 102f)
/`:/db/2/t/ set ([] ti:09:30:00 09:31:00; p:101.5 102.5)

\\
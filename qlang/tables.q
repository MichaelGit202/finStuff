"Finally"
/ section 8 of q for mortals, tables

/ Tables are first-class entities -> they live in memory
/ they are just transposed dictionaries 


"review: flipping your dict creates a table"

t:flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)

"All tables have type 98h"

type t


"accessing a whole col"
t[;`iq]
t[`iq] / this is the same as above
t.name / this is the same as above

"alternative table declaration syntax"
/([] *c1*:*L1*; ...; *cn*:*Ln*)

t:([] name:`Dent`Beeblebrox`Prefect; iq:98 42 126)
/useful for programatic declaration

c1:`Dent`Beeblebrox`Prefect
c2:98 42 126
([] c1; c2)
([] c1:1+til 5; c2:5#42) / Can do anything as long as list is same as column length

"Meta data"
cols t
meta t
/spits out the symbolic namespace of all tables present
tables `.
/spits out t in this case, but if there were more tables, it would spit out all of them
/ record count:
count t


" Flipped Column Dictionary vs. List of Records"
type (`name`iq!(`Dent;98); `weong_name`iq!(`Beeblebrox;42)) /general list (of dictionaries) 0h
type (`name`iq!(`Dent;98); `name`iq!(`Beeblebrox;42)) / a table 98h



"empty tables & schema"
t:([] name:(); iq:())

/its good practice to specify types for the columns
([] name:`symbol$(); iq:`int$())

/ or even better, specify it with the take # operator 
([] name:0#`; iq:0#0)
/0 # `` → An empty list of Symbols

t:([] name:`Dent`Beeblebrox`Prefect; iq:98 42 126)

"SELECT"
/select * equivalent

select from t

/ select a column

select name from t

/divide all iq's by 100
update iq:iq%100 from t

"Doing primary keys"
v:flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)
/ to add a column, you have to create another table with equivalent rows and join them

k:flip (enlist `eid)!enlist 1001 1002 1003

kt:k!v

kt

/how you just do it outright
/ the key table would be a good spot to use til
kt:(flip (enlist `eid)!enlist 1001 1002 1003)! flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)

/or just

kt:([eid:1001 1002 1003] name:`Dent`Beeblebrox`Prefect; iq:98 42 126)

/empty
ktempty:([eid:()] name:(); iq:())

/access via primary key is easy
kt[1002]
kt[1002][`iq]


/kt[1001 1002] <- nope

kt[(enlist 1001;enlist 1002)]

kt[flip enlist 1001 1002]


/z:enlist 1001 1002
/z[0][0] / 1001
/count enlist 1001 1002 -> 1
/enlist 1001 1002      ->   creates , 1001 1002 which in itself is a list
/flip enlist 1001 1002  -> when you flip it it breaks them into their own entries (,1001; ,1002)  both lists

/ like imagine a 1 row matrix with the first one, then the transpose of that flips it 90 degrees with 101 at the top

/ to access multiple rows just do this

kt ([] eid:1001 1002)

/reverse look up, use an anonomouse table + the find op
kts:([eid:1001 1002 1003] name:`Dent`Beeblebrox`Prefect)
kts?([] name:`Prefect`Dent)


"get keys and values"
key kt
value kt
keys kt / gets the name of they key column
cols kt

/promotes the column eid to be the key col
t:([] eid:1001 1002 1003; name:`Dent`Beeblebrox`Prefect; iq:98 42 126)
`eid xkey t

/it will key regardless, this will not error, even though primary kkey fucked up 
t:([] eid:1001 1002 1003 1001; name:`Dent`Beeblebrox`Prefect`Dup)
ktdup:`eid xkey t
/Duplicate key values are not accessible via key lookup.
ktdup 1001
/but are for select
select from ktdup where eid=1001

/ stopping at 8.4.9 Compound Primary Key


\\
"created with a bang (!) operator"
10 20 30 ! 1 2 3

d: `a`b`c!1 2 3

(`Arthur`Dent; `Zaphod`Beeblebrox; `Ford`Prefect)! 100 42 150

key d
value d
count d


"how to make a has table :o"
(`u#`a`b`c)! 10 20 30


"how to make a binary search index / sorted dict"
(`s#`a`b`c)! 10 20 30 / best for time lookup, like i want trades between 10:00 and 10:05

/empty dict
()!()
/ empty typed
(`symbol$())!`float$()

/singletons must enlist keys and values
(enlist `x)!enlist 42

/ this creates a symbol not a singleton
`x!42

"lookup"
d[`a]
d `b
d[`a`c]
ks:`a`c
d ks


"reverse lookup"

d?2

"duplicates values and keys behave weird"
ddup:`a`b`a`c!10 20 30 20
ddup[`a] / we only get the first value for a

/note repeated 20's for reverse lookup
ddup?20 / we get only b

"use where for reverese lookup for non-unique values"

where ddup=20 / get b and c


"dicts can just be anything, you can have lists as the keys"

(`a`b; `c`d`e; enlist `f)!10 20 30

d?20
d `f
"but this leads to wacky reverse lookup behavior"


"dict operations"

/amend a dict value
d:`a`b`c!10 20 30
d[`b]:42

/can be extended via assignment
d[`x]:42
d


"extracting a sub dict using #take op"
d:`a`b`c!10 20 30
`a`c#d

(enlist `c)#d

"remove values with _ or cut"

d:`a`b`c!10 20 30
`a`c _ d
d

`a`c cut d


`a`b`c _ d / remove all keys
.Q.s1 `a`b`c _ d / force display of empty dict, i think it matters for q console

"you can do most if not all the operations on dicts, but they will be applied to the values, not the keys"
/ here is some of the cool stuff


d:`a`b`c!10 20 30
f:{x*x}
f d


"join op"

/ you can just combine them like lists
d1:`a`b`c!10 0N 30
d2:`c`d`e!300 0N 500

/order matters
d1,d2
d2,d1

/coalesce / merge works like lists
d1^d2

"Column dicts"
/ maps a list of symbols to a rectangular lists of lists, ie we are just storing lists in the dict

/we call this a table but sideways
`c1`c2!(`a`b`c; 10 20 30)

/here is a pretensious example
travelers:`name`iq!(`Dent`Beeblebrox`Prefect;42 98 126)
travelers[`name][1]
travelers[`iq][2]

/ better
travelers[`name; 1]
travelers[`iq; 2]


/call a row
travelers[; 2]

/single column
dc1:(enlist `c)!enlist 10 20 30



"we flipping dicts now to make tables"
dc:`c1`c2!(`a`b`c; 10 20 30)
t:flip dc / table
t / mow the table has headers at the top and its indexed vertically

/get entire column c1
dc[`c1;]
dc[;1] / get row 1

"table"
t[;`c1] / get column 1
t[0] / get row 0
t[0; `c1] / get row 0 column 0

/ the guide goons over how tables are transposed dicts and 

\\
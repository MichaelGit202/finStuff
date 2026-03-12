/ section 3 of q for mortals, tables

/Lists are just ordered collections of other atoms and other lists
/ Special cases when a list is uniform



/General list, they use semi colons to separate the items

L1: (1; 1.1; `1)

/note semi colons are used to separate things, not end lines line in cpp & c

L2: (1;2;3;4;5)

/empty list
L3: ()


/nesting
L4: ((1;2;3); ((1;2;3);(4;5); `abc); 1.1)

/There is some blurb in the tutorial talking about how homogenious lists are efficient because the order is obvious, while
/ heterogenious lists are more like sets, like sql and are slower

count L1
count L2
count L3
count L4

"count also just says items of 1 are 1"
count 42
count `getthatpeppaoffthea

"calling first and last"
first L1
last L1

/ homegenious lists are converted to simple lists automatically, mathematically considered a vector
/ However when this happens you cannot append, update, or delete from the list
"simple lists"

/How to tell when its a simple list
"How to tell when its a simple list:"

(100i; 200i; 300i) / when your shit outputs like below
/100 200 300 instead of (100;200;300)
"non simple: "

(100; 200; 300; 1.1)

/ you can also just assign it
/ and give them all the same type like so
L1 : 100 200 300i
L1

"100 200 300~(100; 200 ; 300), this (~) tests for identity, called the match op"


/ The guide then goes through how to make a type of list of every list
"char list"
("s"; "t"; "r"; "i"; "n"; "g")



/"equals vs match"
/"string"="text" / this throws a `length error because = is an atomic operator, item to item comparisons
                / compares s to t and t to e and then runs out

"string"="string"
"string"="btring" / returns an array of 0 1 1 1 1 1, one for each char
"string"~"text"

L:()
L
.Q.s1 L /force it to display the empty list



/ Singletons, a list with one entry, cant do (42) because interpreter
/ thinks its a math operation  (42) = 42
/ so we use the enlist function which boxes its argument into a list
"enlist operator"
enlist 42
/prints out as ,42
/comma denotes its a list

/ "a" = atomic char

enlist "a"
/ this is a string, ie list of chars

enlist (10 20 30; `a`b`c)


L2[0] / indexing into a list, zero based
L2[1] 

L2[1]: 99
L2[1] 

L2[] / print out whole list


/ indexing works how you would expect, but out of bounds erros are not thrown instead you get a typed null
L2[5]
/ 0N


/ double colon creates an empty entry in the list
L[::]
/ this forces a list to be general instead of simple
 
L:(::; 1 ; 2 ; 3)
type L
/outputs a 0h 
.Q.s1 L[0]
/ outputs a ::


"any valid q expression can be in a list construction"
a:42
b:43
(a;b)

l1: 1 2 3 
l2: 40, 50
(l1; l2)
(count l1; sum l2)



/ combining lists, just use a comma
1 2 3, 4 5 / simple list
1 2 3, 4.4 5.5 / general list


/ ensure it becomes a list, also how to enlist an atom
a: 42
a,(1, 2, 3)
(1,2,3), a


/ merging with ^ has to be the same length tho
/ Overwrites the nulls
l1: 10 0N 30
l2: 100 200 0N

"overwrites the nulls"
l1^l2


/ lists as maps
/ the guide goons over how 0 maps to entry 0 

/nesting, lists within lists
L: (1;2;3; (4;5;6); (7;8;9))
count L
/outputs 5

/ then it explains how 2d lists work, like its how you'd expect

m:((11; 12; 13; 14); (21; 22; 23; 24); (31; 32; 33; 34))
m[1][0]

L:(1; (100; 200; (1000; 2000; 3000; 4000)))

L[1][2][0]
/or
L[1;2;0]


/getting multiple entries



/l: 10 20 30 40 50
/l[0 2 4]
/10 30 50

/duplicate and reorder them shits too
l: 0 1 2 3 4 5 6 7 8 9
l[8 7 6 3 1 2 2 2 8 1 0 0 0 0 0 0 0 0 0 22]



"Intro to reshaping lists"
/It is possible to create a (possibly ragged) array of a given number 
/ of rows or columns from a flat list using the reshape operator # by specifying 0N 
/ (missing data) for the number of rows or columns in the left operand.

2 0N#til 10
/ this means make 2 rows from 0 to 9 

/ or you could make an uneven "ragged list" 
0N 3#til 10
/ break the numbers 0-9 into chunks of exactly 3 columns, no matter the rows

-3 #til 10

/ why this is powerful
/Imagine you have a flat list of 1,000,000 trade prices and you want to view them as 
/"1-minute buckets" where each minute has 100 trades. Instead of a loop, you just do:
/all you gotta do 0N 100#prices



"some random stuff about indexing into lists with lists"
01101011b[0 2 4]
"beeblebrox"[0 7 8]


/indicies can live in a variable
l: 0 1 2 3 4 5 6 7 8 9

I : 0 2
l[I]

/ we can index with nested incidces too i guess
l[(0 1 ; 2 3)]


L:100 200 300 400
L[(0 1; 2 3)]


/ man look at this, mass index assignment
L[1 2 3]:2000 3000 4000
/ this is because of the left of right shit, its equivelent to
L[1] : 2000
L[2] : 3000
L[3] : 4000



/ these goobers thought that brackets were too verbose so you can just call them "juxtaposed"
L : 100 200 300 400
L 0

L 2 1

I : 2 1
L I

L ::


"Find operator"
/ overloads the binary ? that returns the index of the first occurence of the right operand
1001 1002 1003 ? 1002
/ 1

L1 : (2,4,6,8)
a: 6
b: -10

L1 ? a
L1 ? b
/ returns 4 like count j

/MORE
1001 1002 1003?1003 1001

m:(1 2 3 4; 100 200 300 400; 1000 2000 3000 4000)
m[1;]


m[1;]~m[1]







\\
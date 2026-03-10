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





\\
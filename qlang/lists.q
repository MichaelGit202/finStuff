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

"100 200 300~(100; 200 ; 300), this tests for identity"







\\
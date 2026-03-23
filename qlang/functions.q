
/ they goon about how functions are a map specified by an algorithm

f:{[x] x*x}
f[3]

/nullary function
f:{42}
/ this just returns 42


/ maximum 8 parameters, greater than that encapsulate them in a list
/ last expression is the return value

f:{[x;y] a:x*x; b:y*y; r:a+b; r}

/this is fine
f:{[x;y] a:x*x; 
    b:y*y; 
    r:a+b;
    r}


f[3;3]

/from guide: functions should stay short and one line, if a function exceeds 20 statements, refactor it

fvoid:{[x] `a set x;}
fvoid 42

"you dont actually need brackets for one var"

f:{x*x}
f 3

`f[5]

.my.name.space.f:{2*x}
`.my.name.space.f[5]

"for some reason they automatically have 3 parameters defined for empty functions, x y z"
g:{x+z}
g[1;2]

/Only use the names x, y and z for the first three parameters of a function, either explicit or implicit.
/evil:{[y;z;x] ...} / don't do this!

"lambda functions"
powers:({1}; {x}; {x*x}; {x*x*x})
selected:2
powers[selected]

"identity function, returns the argument"
:::[`a`b`c]
(::) 42


"functions can be treated like data and can be passed"
b:(1; 98.6; {x*x})

f:{x*x}
(f; neg)
(f; neg)[1; 5]


"functions can be used as the inptut / output of another func"
apply:{x y}
sq:{x*x}
apply[sq; 5]

apply:{[x;y;z] x y + z}
apply[sq; 1; 2] / comes out as 9 because we add 1 and 2 and then square it with sq


"Local and lobal variables"
f:{a:42; a+x} / a is local variable, x is global
f[10] / 52, max level of local vars is 24


"nested helper functions"
/this was NOT suppose to work, but latest version of qlang allows it, so here we are
f:{[p1] a:42; helper:{[p2] a * p2}; helper p1}
f[2]

/ the fix was just pass a in too
f:{[p1] a:42; helper:{[a; p2] a*p2}[a;]; helper p1}
f[2]

/ variables assigned outside of functions are global
b:7
f:{b*x}
f[6]

/only way you can assign a global var in a func
f:{b::x}
f[42]
b

"Function projection"
/ like prefilling a functions arguments
/ like suppose we made this func

add:{x + y} /simple ass func
add:{[x;y] r:x + y; r} / non-qthonic, explicit function, but makes it make more sense

/then we wanted to make a function that just added 10
/projection:
add10: add[10; ]

add10[22]
/note if add changes the projection of add does not 


"operator projection"
(7*)6
-[;42]98



"multiple projections, example"
/ --- 1. Define the General Function ---
/ calcFee[exchange; assetClass; amount]
calcFee:{[ex; cls; amt] 
    base:10.0;                       / flat fee
    mult:$[ex=`NASDAQ; 1.5; 1.0];    / exchange multiplier
    rate:$[cls=`Equity; 0.01; 0.05]; / asset class rate
    base + (amt * rate * mult)
    }

/ --- 2. Step-by-Step Projection ---

/ Step A: Fix the Exchange (Result is a Binary function)
nasdaqFee: calcFee[`NASDAQ; ; ]

/ Step B: Fix the Asset Class (Result is a Unary function)
nasdaqEquityFee: nasdaqFee[`Equity; ]

/ --- 3. Execution ---

/ Now the function only needs the 'amount' to finish
nasdaqEquityFee[5000]   / Returns 85.0
nasdaqEquityFee[10000]  / Returns 160.0

/ --- 4. Alternative: All-in-one Projection ---
/ You can lock both at once without the middle steps
directFee: calcFee[`NASDAQ; `Equity; ]
directFee[5000]         / Returns 85.0


"List of Indices, Keys and Arguments"
d:`a`b`c!10 20 30
ks:`a`c
d ks
/ you can index them with lists like lists


"indexing at depth"
d:`a`b!(1 2 3; 100 200)
d[`a;1]
/ works just about how id expect



"when you access an index that does not exist it reutnrs null like lists"

"you can also apply functions like neg"

(enlist 10)?10


"called atomic functions, seems useful"
f:{(x*x)+(2*x)-1}
/like a list builder
f til 10

"binary functions, as in it comes with 2 arguments"
pyth:{sqrt (x*x)+y*y}
pyth[1;1]

/this applies 1 to all of the y's
pyth[1; 1 2 3]

/nvm this is like one to one 1->1 2->2 3->3
pyth[1 2 3; 1 2 3]

"iterators"
count 10 20 30 /3
count (10 20 30; 40 50) /2 
count each (10 20 30; 40 50) / 3,2
each[count] (10 20 30; 40 50) / 3,2
"iterators on nested lists"
[each[count]] ((1 2 3; 3 4); (100 200; 300 400 500))
(count each) each ((1 2 3; 3 4); (100 200; 300 400 500)) /bruh you have to DRILL
each[each[count]] ((1 2 3; 3 4); (100 200; 300 400 500)) / explicit version of the above


reverse "live"
reverse each ("life"; "the"; "universe"; "and"; "everything")

/ i dont know the point of this
L:enlist 1001 1002 1004 1003
K:enlist each 1001 1002 1004 1003
L[0] / puts 1001 1002 1004 1003 in one entry of a list
K[0] / separate indexes

/flipping a vector to an nx1 matrix
flip enlist 1001 1002 1004 1003

" ' acts as an each with lists"
("abc"; "uv"),'("de"; "xyz")
1,'10 20 30

/it just kinda maps things together, like a zip in python

L1:(enlist `a; `b)
L2:1 2
L1,'L2

/reliable way to make a list of pairs from a pair of lists
flip (L1; L2)

t1:([] c1:1 2 3)
t2:([] c2:`a`b`c)

t1,'t2

"right join operator"
/appending a string to each string in a list
/the enlist is make that one char a string    
("abc"; "de"; enlist "f") ,\: ">"

"</" ,/: ("abc"; "de"; enlist "f")


"cross product"
cp:1 2 3,/:\:10 20
/with the right and left join you get close
/ but we need the raze
cp
cp:raze cp
cp

/or just fuckin
1 2 3 cross 10 20

/transposed cross product
raze 1 2 3,\:/:10 20


"OVER OPERATOR"
/ the over iterator which is the forward slash
0 +/ 1 2 3 4 5
/not specifying the starting value makes it more qthonic
(+/) 1 2 3 4 5 6 7 8 9 10

"accumulator + printf example"
/accumulator example, the 0N! prints out each step 
addi:{0N!(x;y); x+y}
0 addi/ 1 2 3 4 5


"max-min"
(|/) 7 8 4 3 10 2 1 9 5 6 / maximum 
(&/) 7 8 4 3 10 2 1 9 5 6 / minimum

"removing top level of nesting"
(,/)((1 2 3; 4 5); (100 200; 300 400 500))
raze ((1 2 3; 4 5); (100 200; 300 400 500)) /same thing

f:{2*x+y}
100 f/ 1 2 3 4 5 6 7 8 9 10
(f/) 1 2 3 4 5 6 7 8 9 10

"computing n-th fibonacci number with over"
fib:{x,sum -2#x}
fib/[10; 1 1]

"derivative approximation"
/yea i kinda get it but my mind is too blown rn
/ TODO come back
f:{-2+x*x}
secant:{[f;x;e] (f[x+e]-f x-e)%2*e}
{x-f[x]%secant[f; x; 1e-6]}/[1.5]


"infinite loop with newton forward ie newton-raphson"
newtcycle:{[xn] xn-((xn*xn*xn)+(-2*xn)+2)%-2+3*xn*xn}
newtcycle/[0.0]
/q detects cycles by matching previous recursive results and stops itself
/ before if fucks up


"while loop equivalent"
fib:{x,sum -2#x}
fib/[{1000>last x}; 1 1]
    /our while condition, so this says go till the last element of x is greater than 1000 
    / x is our list that keeps growing as we calculate the next fib number, so we keep going until the last one is greater than 1000

"SCAN OPERATOR "
/ is exactly the same as over except it reurns all intermediate results

10 fib\ 1 1
100 f\1 2 3 4 5 6 7 8 9 10


\\

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




\\
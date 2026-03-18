
"til creates a list of numbers, starts at 0"
til 10
2 * til 10 / multiply everything by 2
til 3
-5+4*til 3 / multiply by 4 then subtract 5

"distinct returns the unique values in a list"
distinct 1 2 4 3 5 5 5 6 6 6 1 2 3 4

where 101010b
/returns the indices of 1b in a bool list

L: 10 20 30 40 50 60

L[where L > 20]: 2222 / its kinda like a sql statement but for lists, returns indices 
L

/ groups a list into a dictionary with unique values as keys and lists of indices as values
group L
group "mississippi"


/ you cant do more than 2 values in these lists
/ sum two together
+[1;2]

/ equality of two
=[2;3]

(2+)3

neg 1 2 3

1 2 3+10 20 30

100+(1 2 3; 4 5)

sum 1 2 3

"the gocha of left-of-right eval"
/ because pemdas does not exist and it evaluates "right of left"
/ ie right to left, we get this bs
/ while these should be the same, they are not
2 * 3 + 4
(2*3) + 4
4 + (2*3)

/sometimes you just gotta use em
(2+3)*3+4


(())~enlist () / false
4 2~2 4
4 2~4 2

42~(42) / common mistake, not a singleton
42~ enlist 42 / singleton

/ match checks that it is the same type and value
/ equality compares the value

"equal"
42=42i
42=42.0
42=0x42
42=0x2a / hex 2a is 42 in decimal
42="*"

/`a="a" <- type error

"not equal"
/not equal
not 42=98.2


/ comparing floats goes up to 10^-14
r: 1%3
r
2=r+r+r+r+r+r

"not everything"
not 0 / not 0 is true
not 0b
not 1b
not 0xff
not 98.1

/every not char is going to return false except the underlying value of 0
"char"
not "a"
not "" / since this is a char list we ask q to invert an empty list, so it gives us an empty list of bools, ie `boolean$()
not "*"
not "\000"

/ for temporal, midnight is 0, or january 2000 for dates
/ i aint copying it down



/ < > <= >= work for all compatible types

4 < 42
4h > 0x2a
-1.4142<99i

/ for chars its compares their numeric values

"all numeric ascii chars"
16 16#"c"$til 256

/ symbol comparison is lexicographic order

`a < `b /true
`abc < `aba /false c is greater than a


/they all work on lists too
 
2 1 3=1 2 3
"zaphod"="Arthur"
2=1 2 3
10 20 30<=30 20 10


/arithmatic is basically the same
/ but %  is division and mod is modulus
10%2
10 mod 3

/ then it showcases a bunch of ways stuff gets promoted, basically if it has more bits it gets promoted to that
/  ie everything turns into floats

/OVERFLOW
9223372036854775806+4
2*5223372036854775800
/UndA flow
-9223372036854775806-4


/ dont use - to negate, use neg


"greater and less"
42|43 /greater 
98.6&101.9 / less
2|0 1 2 3 4
/ can be used for bitwise operations on bool lists
11010101b|01100101b / OR
11010101b&01100101b / AND
11010101b^01100101b / XOR
not 11010101b / NOT

"fill operator fills null values"
/ ^ is the fill operator
42 ^ 0N 
0 ^ 1 2 0N 4 0N

"ammend, operate and assign"
/ the equivalent in c as x += 1
x:42
x+:1
x

x-:1
x&:21
x

L:100 200 300 400
L[1]+:99
L

L[1 3]-:1
L

"appending to a list, has to be same type"
L:1 2 3
L,:4
L

"sqrt, exp, log work just about how you think they do exp and log are base e"
exp 1
exp 2
log exp 1

"exexp is just x to the power of y"
2 xexp 5

"xlog works the same"


"div is integer division, just rounded down"
7 div -2 / this equals -4, because it rounds down, not towards 0, which is so stupid
7 div 2 / this equals 3

"mod"
7 mod 2.5
3 4 5 mod 2

"signum, ie get the sign"
signum 42 /1i
signum -42.0 /-1i


"floor ceil abs work as expected"

"recipropcal"
reciprocal 2


"casting with ` and $"
`int$1999.12.03
`int$2013.01m

"null symbol is less than any other symbol"
`a<`

"aliases"
a:10
b:10
c::a
c

w::a + b
w

a:20
c
w

"how to print "
x:3
y:4
w::(0N!x*x)+y*y 
x:4
w / when called it prints out 2, because it printx x*x and then the final result because of the identity function

"system dictionary"
.z.b
/ this stores a dictionary of all the variables in the current scope, and their values, so you can see what you have defined
/ but it also illustrates the dependancies between w and a and b. A dependancy graph can blow up real fast
\\

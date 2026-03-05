/This is for sections 2 - 5 of the Q For mortals guide at code.kx.com


/single line comment

10; / inline comment

/
 block comment
\

"hello world"


/ assignment
/varible name : data


/INTS there are 3 types of integers in q
"ints"
/ 8 byte int
a:42
/or, redundantly
42j

/ 2 byte int, called a short
-123h

/ 4 byte int
1234567890i 



/floats, just IEEE standard 8 byte float, also claled a double, 15 dec
"floats"
3.1415265
1f
1.0


/scientific notation
1.234e7
1.234e-7


/Real numbers
/noted by the devs as 'useless' in finance, 6 dec
a:12.34e / yes is is akward that it uses e like in scientific notation


/q console displays defaults to seven digits by rounding the 7th digit
/you can change this using P

"change console rounding"
f12:1.234578901211
f16:1.2345677777777777

\P 12
f12
f16

\P 16
f12
f16

\P 0

1%3




/===============BINARY DATA===============

/no key words for true or false
true: 0b
false: 1b

/ implicitly promoted to unsigned ints when in arithmetic expressions
/ this yields an int
"binary to int and float"

42+0b
/this yields a float
3.1415+0b

/Noted by the doc, "the ability of booleans to participate in arithmetic can be useful in eliminating conditionals"
/ex
"branchless programming"
sizes: 499
total: sizes + 50 * sizes > 500
total

sizes: 501
total: sizes + 50 * sizes > 500
total



/bytes
"byte data"
/8 bit value definted by 0x (hex digits)
0x2a

/signed 
1+0x29



/guid
"Guids"
/null guid value 0Ng
aListOfGuids:1?0Ng
1?0Ng

/importing a guid generated elsewhere
"G"$"61f35174-90bc-a48a-d88f-e15e4a377ec8"


/ ascii but with numbers
"\142"

/symbol is an atom that holds text, akin to a VARCHAR, irreducible
`q
`zaphod

/this is to show they are the same, operator called match operator
`a~"A"

`$"A symbol with blanks and a back tick `"
/ above $ is casting a list of characters (right) to a symbol (left)


"Temporal data"
2025.02.16

2000.01.01=0
/comes out as true

2000.01.02=1

a:1999.12.31=-1

/cast it back to days
"int cast"
`int$a


"time types from midnight"

/hh:mm:ass:uuu
milleseconds: 12:34:56.789
milleseconds

/0dhh:mm:ss.nnnnnnnnn
nanoseconds: 12:34:56.123456000; /microseconds become nano
nanoseconds


/there are more time types like date-time one depricated one new



/im not typing all that shit out
/a month type of months since millenium


/ an minute type of minues from midnight

/ a second type of seconds from midnight


"nulls and infs"

0w /pos inf float   
0W /pos long int  aka 9223372036854775808

0n / null float
0N / null long int aka -9223372036854775807

"negative infinity is one less than null"
-0W > 0N


"testing for nulls"
null 42
null `
null " "
null ""



\\
end of file maker above, everything below is ignored so this is technically a comment

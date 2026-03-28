"file handleing"
/paths, easier to do with strings, but if you are using symbols you gotta use a trailing colon to do it correctly
/ hsym does this when casting a string to a symbol

hsym `$"/data/file name.csv"
/`:/data/file name.csv

/ok if you have an issue with path, a leading forward slash assumse bottom of drive
/ :data/a relative
/ :/data/a absolute
path: hsym `$"/home/mica/finProject/finStuff/qlang/data/example.csv"

/size check
hcount path
hcount `:data/example.csv
hcount `:./data/example.csv / explicite relative

/use hdel to delete

"Serializing and Deserializing q Entities"
/you can serialize anything
`:data/a set 42
`:data/L set 10 20 30
/table
`:data/t set ([] c1:`a`b`c; c2:10 20 30)

"reading in the data"
get `:data/a
get `:data/L
get `:data/t

/alternatively just use value
value `:data/t

/alternativaly use the shorthand to read in a file and delcare a variable with the same name as that file
\l data/t
t


"opening binary files"
`:data/L set 10 20 30

/open a data file w/ hopen
h:hopen `:data/L

/writing to a file 
h[42]
h 100 200

hclose h

get `:data/L

h:hopen `:data/L
h 43 /8i <- id of the connection to the file. recall 0 1 2 is like keyboard, mouse, and screen, its the file descriptor
8i[1 2 3 4] / valid way to write to it
hclose h


/read1 to read a list of bytes
"read1 for bytes"
read1 `:data/L set 10 20 30

/another way to write to a file
.[`:data/raw; (); :; 1001 1002 1003]
get `:data/raw

/append
.[`:data/raw; (); ,; 42]
get `:data/raw


"Saving and loading on tables"
t:([] c1:`a`b`c; c2:10 20 30; c3:1.1 2.2 3.3)
save `:data/t
load `:data/t

t

/can al;so do this for a better view of the table
save `:data/t.txt
save `:data/t.csv
save `:data/t.xml
save `:data/t.xls / hell yea


"splayed tables"
/splitting a table into columns and saving each column as a separate file

"splitting"
`:data/tsplay/ set ([] c1:10 20 30; c2:1.1 2.2 3.3)
/get meta data
"--metadata--"
get hsym `$"data/tsplay/.d"

/columns of arbitrary lists cannot be splayed, Symbol columns must be enumerated.

"enumerating a symbol column"
/you can enumerate a symbol column the manual way that Kx documentation tells you to
/ store the resulting sym list in the root directory – i.e., one level above the directory holding the splayed table.

`:data/tsplay/ set ([] `sym?c1:`a`b`c; c2:10 20 30)
sym
`:data/sym set sym

/instead you do it like a normal person and use the built in function to enumerate a symbol column
`:data/tsplay/ set .Q.en[`:data/; ([] c1:`a`b`c; c2:10 20 30)]

/stopped at 11.4 Text Data

\\
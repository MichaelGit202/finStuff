"covers the general application section of QFM because this is like relearning everything the 'correct' way "

"General applies @ operator, this is apply at a single level"
/indexes
10 20 30 40@1

L:10 20 30 40
L@1

@[L;1] / standard form

count@L


{x*x}@L

d:`a`b`c!10 20 30
d@`a

@[d;`b]


f:{6*7}
@[f; ::]


"Apply operator, this is apply at depth"

L:(10 20 30; 40 50)

L[1; 0]
L . 1 0

d:`a`b`c!(10 20 30; 40 50; enlist 60)
d . (`b; 0)

f:{x*x}
f . enlist 5
f . enlist 1 2 3


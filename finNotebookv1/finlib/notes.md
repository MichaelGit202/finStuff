## Notes for the libs development


### General comments

>3/3/26 Data manipulation fucking sucks
----
 So basically what im dealing with is the fact that all the data I find is in slightly different formats, so live csv's differ form json and none of them are standardize. This fucking sucks since I want to do the KDB database and I dont know Q yet, and I dont want to go through the headache of making a fucking sql database. So I dont have a central place to reformat and store to like a real DBA. Honestly I just need like a little bit of data to fuck around with algo's while I learn Q in the mean time, THEN FINALLY, I can make this library not SUCK ASS with the data import. It also sucks that I just spent a bunch of time implementing csv reading just for it to suck.
## Notes for the libs development


### General comments

>3/3/26 Data manipulation fucking sucks
----
 So basically what im dealing with is the fact that all the data I find is in slightly different formats, so live csv's differ form json and none of them are standardize. This fucking sucks since I want to do the KDB database and I dont know Q yet, and I dont want to go through the headache of making a fucking sql database. So I dont have a central place to reformat and store to like a real DBA. Honestly I just need like a little bit of data to fuck around with algo's while I learn Q in the mean time, THEN FINALLY, I can make this library not SUCK ASS with the data import. It also sucks that I just spent a bunch of time implementing csv reading just for it to suck.

>3/4/26 In market and sim i have it setup weird where you have to add cash to the sim before buying, change? NAH
---
 I gotta figure out how im going to fit strategies into this, Its confusing how im gong to do that, I could make them an object i pass into the market object, which then kinda defeats the point of the jupiter notebook, but I could also have them be both optional where you do it in a NB but you gotta have a for loop but also have a way to pass in a strategy and have that be automated. I like that idea

- like have a function called, run_strategy(strategy)
- but also have manual running with step()

>3/12/26
---
 This shit kinda weird, so each stock sim reads in chunks of the historical price data and works like each sim is its own portfolio,
 - Currently, I do not store the portfolio value
 - I do not store the full stock history, just shifting from chunk-to-chunk
 - Visuals require a history of portfolio performance and stock history
    - Storing both of these in ram = bad idea for scale
    - If stock history is already stored then all you need to re-query for analysis / visuals is start / end, additionally data resolution can be scaled down
    - a portfolios performance needs to be temporarily stored somehow

- Solution: store portfolio value in DuckDB or SQLite
- Have a timeRange stored for time data
- convert json data to parquet
- At some point convert shid over to polars


### saved prompts

>Im saving this when I goahead and implement visuals

whats the best way I could do some visuals in this stock simulator, I dont want you to like do anything yet I just want advice. 
I need
1. libraries
2. a method of integrating these libraries

What I want visually is a graph with the price history, showing drawdown, max draw down, the ability to visualize portfolio performance.

I also want suggestions for what to display and how.


### libraries
https://pola.rs/ : pandas but better
QuantStats : either integrate or steal ideas from them
Dash: seems better than streamlit and its built ontop of flask
Plotly: for plotting
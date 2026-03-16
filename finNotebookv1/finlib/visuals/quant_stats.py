import quantstats as qs
import pandas as pd

def returns_report(returns_df):
    returns = returns_df['value'].pct_change()
    # Generate the report
    qs.reports.html(returns, output='sim_results.html')
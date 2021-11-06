import pandas as pd
# %%
nba = {}

for year in range(2001, 2022):
    url_nba = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + ".html#advanced-team"
    if (year >= 2016):
        data_nba = pd.read_html(url_nba)[10]
    else:
        data_nba = pd.read_html(url_nba)[8]
    nba[year] = data_nba
    nba[year].columns = nba[year].columns.droplevel()
    nba[year] = nba[year][:-1]
    nba[year].loc[:, ('Team')] = nba[year]['Team'].str.split('*', expand=True)[0]
    
    url_vegas = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_preseason_odds.html"
    data_vegas = pd.read_html(url_vegas)
    data_vegas = data_vegas[0]
    
    nba[year] = nba[year].merge(data_vegas[["Team", "W-L O/U"]],
                left_on="Team", right_on="Team")
      
# %%






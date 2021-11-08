# %% import packages
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import seaborn as sns
# %% import and clean data
nba = {}

for year in range(2005, 2022):
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
    
    nba[year]["wpct"] = nba[year]["W"]/(nba[year]["W"]+nba[year]["L"])
    if (year == 2021):
        nba[year]["vegas_wpct"] =  nba[year]["W-L O/U"]/72
    elif (year == 2012):
        nba[year]["vegas_wpct"] =  nba[year]["W-L O/U"]/66
    else:
        nba[year]["vegas_wpct"] =  nba[year]["W-L O/U"]/82
    
    nba[year] = nba[year].drop(columns = ['Unnamed: 17_level_1',
                                          'Unnamed: 22_level_1',
                                          'Unnamed: 27_level_1',])
    
    nba[year].columns = ['Rk', 'Team', 'Age', 'W', 'L', 'PW', 'PL', 'MOV',
                         'SOS', 'SRS', 'ORtg', 'DRtg', 'NRtg', 'Pace', 'FTr',
                         '3PAr', 'TS%', 'OeFG%', 'OTOV%', 'ORB%', 'OFT/FGA', 
                         'DeFG%', 'DTOV%', 'DRB%', 'DFT/FGA', 'Arena', 'Attend.',
                         'Attend./G', 'W-L O/U', 'wpct', 'vegas_wpct']
    yr = [year] * 30
    nba[year]["year"] = yr
    
    nba[year]["adj_3PAr"] = nba[year]["3PAr"] - nba[year]["3PAr"].mean()
    nba[year]["adj_TS%"] =  nba[year]["TS%"] - nba[year]["TS%"].mean()
    
data = pd.concat([nba[2005], nba[2006], nba[2007], nba[2008], nba[2009],
                  nba[2010], nba[2011], nba[2012], nba[2013], nba[2014],
                  nba[2015], nba[2016], nba[2017], nba[2018], nba[2019],
                  nba[2020], nba[2021]])

#%%
x = np.array([data["OeFG%"], data["OTOV%"], data["ORB%"], data["OFT/FGA"],
              data["DeFG%"], data["DTOV%"], data["DRB%"], data["DFT/FGA"]]).transpose()

y = np.array(data["wpct"])

lm = LinearRegression().fit(x, y)
r_sq = lm.score(x, y)

data["predict"] = lm.predict(x)

predict_by_year = data.groupby("year")["predict"].mean()

# %%

threes = data.groupby("year").mean()[["3PAr", "TS%"]]
sns.relplot(data = threes, x = "year", y = "3PAr")
sns.relplot(data = threes, x = "year", y = "TS%")

data["over"] = (data["wpct"] > data["vegas_wpct"])*1
sns.relplot(data = data, x = "adj_3PAr", y = "vegas_wpct", hue = "over")

data["high_3PAr"] = (data["adj_3PAr"] > 0)*1
data["high_TS%"] = (data["adj_TS%"] > 0)*1
data["high_total"] = (data["vegas_wpct"] > 0.5)*1
data["old"] = (data["Age"] > data["Age"].mean())*1

pivot = data.groupby(["high_3PAr", "high_total"]).agg(["mean", "sum","count"])["over"]
print(pivot)

#sns.relplot(data = data[data["Team"]=="Houston Rockets"], x = "year", y = "3PAr")

# %% Code from Elliot

#plot = sns.regplot(x = predict_by_year.index, y = predict_by_year.values, data = predict_by_year)

data["Odds_Error"] = data["wpct"] - data["vegas_wpct"]

error_by_year = data.groupby("year")["Odds_Error"].mean()

e_plot = sns.regplot(x = error_by_year.index, y = error_by_year.values, data = error_by_year)

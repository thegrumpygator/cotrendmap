import numpy as np
import pandas as pd

from pathlib import Path

import seaborn as sns
import matplotlib.pyplot as mplt
import matplotlib.dates as mdates

# Helper Functions - entity access

def fips_for_group(data, group="DC Metro"):
    fips_list = []
    for fip in data[data['group']==group]['fips']:
        for fi in fip:
            fips_list.append(fi)
    return fips_list

def fips_for_state(data, state='VA'):
    fips_list = []
    for fip in data[data['state'] == state]['fips']:
        for fi in fip:
            fips_list.append(fi)
    return fips_list

def fips_for_county(data, county='Fairfax'):
    fips_list = []
    for fip in data[data['county'] == county]['fips']:
        for fi in fip:
            fips_list.append(fi)
    return fips_list

def frame_from_group(data_covid, data_groups, group="DC Metro"):
    fipslist = fips_for_group(data_groups, group)
    
    # filter the frame
    df = data_covid[data_covid.fips.isin(fipslist)]
    
    # get group population
    pop2020 = sum(data_groups[data_groups['group'] == group]['pop'])
    
    # derive new columns
    df = df.groupby(['date'])[['cases', 'deaths']].agg('sum').diff().reset_index()
    
    df['cases_7d'] = df.cases.rolling(7).mean().shift(-3)
    df['cases_100k'] = df['cases'] / pop2020 * 100000
    df['cases_7d_100k'] = df['cases_7d'] / pop2020 * 100000
    df['deaths_7d'] = df.deaths.rolling(7).mean().shift(-3)
    
    return df

def mpl_plot_from_group(df_covid, df_entity, group="DC Metro", ymax=80):
    df = frame_from_group(df_covid, df_entity, group)
    fig = mplt.figure(figsize=(14, 10))
    sns.lineplot(x="date",
                 y="cases_100k",
                 label="Daily",
                 data=df,
                 ci=None,
                 alpha=0.4)

    plot_ =  sns.lineplot(x="date",
                          y="cases_7d_100k",
                          label="7-Day Average",
                          data=df)
    fig.canvas.draw()
    mplt.legend()
    mplt.xlabel("Date", size=14)
    mplt.ylabel("Daily New Cases per 100,000 population", size=14)
    mplt.ylim(0, ymax)

    new_ticks = [i.get_text() for i in plot_.get_xticklabels()]
    mplt.xticks(range(0, len(new_ticks), 3), new_ticks[::3], 
               rotation=60, 
               fontweight='light', 
               fontsize="x-small")

    return

def mpl_plot_from_group_d(df_covid, df_entity, group="DC Metro", ymax=80):
    """Modify for x-axis as dates"""

    df = frame_from_group(df_covid, df_entity, group)

    mplt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    mplt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    mplt.plot(df["date"], 
              df["cases_100k"], 
              'bo',
              label="Cases/100K",
              markersize=15,
              alpha=.3)

    mplt.plot(df["date"], 
              df["cases_7d_100k"], 
              'r',
              label="Cases/100K (7-Day-Ave)")

    mplt.plot(df['date'],
              df['deaths_7d'],
              'k-',
              label="Deaths (7-Day-Ave)"
              )

    mplt.gcf().autofmt_xdate()
    fig = mplt.gcf()
    fig.set_size_inches(12, 8)
    mplt.ylim(0,ymax)
    mplt.title(group)
    mplt.legend()
    mplt.xlabel("Date", size=14)
    mplt.ylabel("Daily New Cases per 100,000 Population", size=14)
    return
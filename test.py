import numpy as np
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup as bs
import folium
import webbrowser


def get_forecast_province(province):

    url = "https://www.weather-forecast.com/locations/{0}/forecasts/latest".format(province)
    r = requests.get(url)
    forecast = bs(r.content, "lxml")

    ###### get day name
    wthr = forecast.findAll("div", {"class": "b-forecast__table-days-name"})
    lstDayName = []
    for i in wthr:
        lstDayName.append(i.text)


    #### get date
    wthr1 = forecast.findAll("div", {"class": "b-forecast__table-days-date"})
    lstDate = []
    for i in wthr1:
        lstDate.append(i.text)

    ##### get time
    lstTime = []
    wthr2 = forecast.findAll("tr", {"class": "b-forecast__table-time js-daytimes"})
    for item in wthr2:
        lst = []
        for i in item.findAll("td"):
            if i.has_attr("class") and re.search("forecast__table-time-item", i["class"][0]).start() != None:
                x = i.findAll("span", {"class": "b-forecast__table-value"})
                lst.append(x[0].text.replace(u"\u2009", " "))

                if len(i["class"]) > 1 and re.search("forecast__table-day-end", i["class"][1]) != None:
                    lstTime.append(lst)
                    lst = []

    ##### get humidity
    wthr3 = forecast.findAll("tr", {"class": "b-forecast__table-humidity js-humidity"})
    lstHumidity = []

    for item in wthr3:
        lst = []
        for i in item.findAll("td"):
            x = i.findAll("span", {"class": "b-forecast__table-value"})
            lst.append(x[0].text)

            if (i.has_attr("class")) and (i["class"][0] == "b-forecast__table-day-end"):
                lstHumidity.append(lst)
                lst = []

    # print dataframe to file
    df_forecast = pd.DataFrame(dict({"dayname": lstDayName, "date": lstDate, "time": lstTime, "humidity": lstHumidity}))
    df_forecast["count"] = df_forecast.apply(lambda row: len(row["humidity"]), axis = 1)

    ### avg humidity
    df_forecast = df_forecast[["date","humidity","count"]].sort_values(["date","count"], ascending = [True, False])
    idx = df_forecast.groupby(['date'])['count'].transform(max) == df_forecast['count']
    df_forecast_avg = df_forecast[idx]
    df_forecast_avg['avg_humidity'] = df_forecast_avg.apply(lambda row: avg_humidity(row), axis = 1)
    df_forecast_avg['province'] = province


    return df_forecast_avg[['date','province','avg_humidity']]

def avg_humidity(row):
    lst = [int(i) for i in row['humidity']]
    return np.mean(lst)

def long_lat():
    # how are you
    df_long_lat = pd.DataFrame({'province':["Nhatrang","Danang","Hanoi","Hochiminh"], \
                                'lat':[12.235192,16.06778,20.984068,10.762622], 'lon':[109.193554,108.22083,105.862511,106.660172]})
    return df_long_lat


def plot_map(df_forecast_all, df_long_lat):

    df_plot =  df_forecast_all.merge(df_long_lat, on = "province", how = 'inner')
    print(df_plot)

    df_plot = df_plot[df_plot['date'] == '10'].reset_index()
    df_plot['infor'] = df_plot.apply(lambda row: row["province"] + "\n" + str(int(row["avg_humidity"])) + "%", axis = 1)

    m = folium.Map(location = [16.06778,104.112511], zoom_start= 5.5)
    mark = folium.map.Marker(location=[21.797548,108.22083], popup='Da Nang')

    for i in range(0, len(df_plot)):
        folium.Marker(
            location=[df_plot.iloc[i]['lat'], df_plot.iloc[i]['lon']],
            popup=df_plot.iloc[i]['infor'],
        ).add_to(m)

    m.save("map.html")
    webbrowser.open("map.html")

    return df_plot

if __name__ == '__main__':

    pd.set_option('display.max_columns', 10)
    provinces = ["Nhatrang","Danang","Hanoi","Hochiminh"]
    df_long_lat = pd.DataFrame({'province': ["Nhatrang", "Danang", "Hanoi", "Hochiminh"], \
                                'lat': [12.235192, 16.06778, 20.984068, 10.762622],
                                'lon': [109.193554, 108.22083, 105.862511, 106.660172]})
    df_forecast_all = pd.DataFrame()

    for p in provinces:
        df_forecast = get_forecast_province(p)
        if df_forecast_all.empty:
            df_forecast_all= df_forecast
        else:
            df_forecast_all = pd.concat([df_forecast_all, df_forecast])

    plot_map(df_forecast_all,df_long_lat)





import pyodbc
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import duhi_query

server = '192.168.20.5'
database = 'IZH_SQL_2018'
username = 'sa'
password = ''
with pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    # conn.row_factory = pyodbc.Row
    cur = conn.cursor()
    s = duhi_query.query_sale("'20180101'", "'20220430'", "'  2KL0   '")
    # print(s)
    cur.execute(s)
    rows = cur.fetchall()
    # # print(rows)
    for row in rows:
        print(row)
exit()

path_dir = pathlib.Path('d:/py/ml')
path_xls = pathlib.Path(path_dir, 'ml_духи.xls')
path_plt = pathlib.Path(path_dir, 'ml_духи.png')

# читаем файл, подготавливаем данные
df = pd.read_excel(io=path_xls, engine='xlrd')
df['Сумма'] = round(df['Сумма'] / 1000, 0)

def graph(arr):
    # строим график продаж по месяцам
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    sns.lineplot(data=arr, x='Месяц', y='Сумма', hue='Год', palette='plasma')
    plt.grid(True)
    plt.title('Продажи по месяцам')
    plt.ylabel('Сумма, тыс. руб.')
    plt.savefig(path_plt, dpi = 150)

def predict(arr, year, month):
    X = arr.query('Месяц == @month')
    y = X.loc[:, 'Сумма'].values
    X = X.loc[:, 'Год'].values.reshape(-1, 1)
    # model = LinearRegression()
    model = RandomForestRegressor()
    model.fit(X, y)
    X_new = [[year]]
    return round(model.predict(X_new)[0], 0)

def fill(arr):
    while 1:
        yr = max(arr['Год'])
        mn = max(arr.query('Год == @yr')['Месяц']) + 1
        if mn > 12:
            break
        pred = predict(arr, yr, mn)
        data = pd.DataFrame({'Год': [yr],
                            'Месяц': [mn],
                            'Сумма': [pred]})
        arr = pd.concat([arr, data], ignore_index=True)
    return arr

# graph(df)
# arr = fill(df)
# print(arr)
# graph(arr)







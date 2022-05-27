import pyodbc
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

WORK_DIR = pathlib.Path('d:/py/ml')
CURR_DIR = pathlib.Path.cwd()
FILE_XLS = pathlib.Path(WORK_DIR, 'ml_духи.xls')
FILE_GPH = pathlib.Path(WORK_DIR, 'ml_духи.png')
FILE_QRY = pathlib.Path(CURR_DIR, 'query.txt')

SERVER = '192.168.20.5'
DATABASE = 'IZH_SQL_2018'
USERNAME = 'sa'
PASSWORD = ''

dB = "'20180101'"
dE = "'20220430'"
gruppa_id = "'  2KL0   '"

def read_query():
    with open(FILE_QRY, 'r', encoding='utf-8-sig') as f:
        str_qry = ''.join([s for s in f])
    str_qry = str_qry.replace('<dB>', dB)
    str_qry = str_qry.replace('<dE>', dE)
    str_qry = str_qry.replace('<gruppa_id>', gruppa_id)
    return str_qry

def exec_query(str_qry):
    with pyodbc.connect('DRIVER={SQL Server};SERVER=' + SERVER +
                        ';DATABASE=' + DATABASE +
                        ';UID=' + USERNAME +
                        ';PWD=' + PASSWORD) as conn:
        return pd.read_sql(str_qry, conn)

def graph(arr):
    # строим график продаж по месяцам
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    sns.lineplot(data=arr, x='MONTH', y='SUMMA', hue='YEAR', palette='plasma')
    plt.grid(True)
    plt.title('Продажи')
    plt.xlabel('Месяц')
    plt.ylabel('Сумма, тыс. руб.')
    plt.savefig(FILE_GPH, dpi = 150)

def predict(arr, year, month):
    X = arr.query('MONTH == @month')
    y = X.loc[:, 'SUMMA'].values
    X = X.loc[:, 'YEAR'].values.reshape(-1, 1)
    model = RandomForestRegressor()
    model.fit(X, y)
    X_new = [[year]]
    return round(model.predict(X_new)[0], 0)

def fill_array(arr):
    while 1:
        yr = max(arr['YEAR'])
        mn = max(arr.query('YEAR == @yr')['MONTH']) + 1
        if mn > 12:
            break
        pred = predict(arr, yr, mn)
        data = pd.DataFrame({'YEAR': [yr],
                            'MONTH': [mn],
                            'SUMMA': [pred]})
        arr = pd.concat([arr, data], ignore_index=True)
    return arr

str_qry = read_query()
arr = exec_query(str_qry)
# читаем файл, подготавливаем данные
# df = pd.read_excel(io=FILE_XLS, engine='xlrd')
arr['SUMMA'] = round(arr['SUMMA'] / 1000, 0)
# graph(df)
arr = fill_array(arr)
print(arr)
graph(arr)

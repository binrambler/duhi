import pyodbc
import pathlib
import configparser
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

CURR_DIR = pathlib.Path.cwd()
FILE_IN0 = pathlib.Path(CURR_DIR, 'duhi.ini')
FILE_IN1 = pathlib.Path(CURR_DIR, 'query.ini')
FILE_XLS = pathlib.Path(CURR_DIR, 'ml_духи.xls')
FILE_GPH = pathlib.Path(CURR_DIR, 'ml_духи.png')
FILE_QRY = pathlib.Path(CURR_DIR, 'query.txt')

SERVER = ''
DATABASE = ''
USERNAME = ''
PASSWORD = ''

DATE_BEG = ''
DATE_END = ''
GRUPPA_ID = ''

def create_ini(mode, file_ini):
    config = configparser.ConfigParser()
    if mode == 'setup':
        config.add_section('Main')
        config.set('Main', 'server', '192.168.20.5')
        config.set('Main', 'database', 'IZH_SQL_2018')
        config.set('Main', 'username', 'sa')
        config.set('Main', 'password', '')
    elif mode == 'query':
        config.add_section('Main')
        config.set('Main', 'date_beg', "'20180101'")
        config.set('Main', 'date_end', "'20220430'")
        config.set('Main', 'gruppa_id', "'  2KL0   '")
    with open(file_ini, 'w') as f:
        config.write(f)

def read_ini():
    if not FILE_IN0.exists():
        print('Нет файла с настройками программы:', FILE_IN0)
        create_ini('setup', FILE_IN0)
        return
    if not FILE_IN1.exists():
        print('Нет файла с настройками запроса:', FILE_IN1)
        create_ini('query', FILE_IN1)
        return
    config = configparser.ConfigParser()
    config.read(FILE_IN0)
    global SERVER, DATABASE, USERNAME, PASSWORD
    SERVER = config.get('Main', 'server')
    DATABASE = config.get('Main', 'database')
    USERNAME = config.get('Main', 'username')
    PASSWORD = config.get('Main', 'password')

    config.read(FILE_IN1)
    global DATE_BEG, DATE_END, GRUPPA_ID
    DATE_BEG = config.get('Main', 'date_beg')
    DATE_END = config.get('Main', 'date_end')
    GRUPPA_ID = config.get('Main', 'gruppa_id')

def read_query():
    with open(FILE_QRY, 'r', encoding='utf-8-sig') as f:
        str_qry = ''.join([s for s in f])
    str_qry = str_qry.replace('<DATE_BEG>', DATE_BEG)
    str_qry = str_qry.replace('<DATE_END>', DATE_END)
    str_qry = str_qry.replace('<GRUPPA_ID>', GRUPPA_ID)
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

read_ini()
str_qry = read_query()
arr = exec_query(str_qry)
# читаем файл, подготавливаем данные
# arr = pd.read_excel(io=FILE_XLS, engine='xlrd')
arr['SUMMA'] = round(arr['SUMMA'] / 1000, 0)
# graph(df)
arr = fill_array(arr)
print(arr)
graph(arr)

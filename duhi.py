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
FILE_QRY = pathlib.Path(CURR_DIR, 'query.txt')

SERVER = ''
DATABASE = ''
USERNAME = ''
PASSWORD = ''

DATE_BEG = ''
DATE_END = ''
GRUPPA_CODE = ''
GRUPPA_NAME = ''

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
        config.set('Main', 'gruppa_code', "'0002'")
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
    global DATE_BEG, DATE_END, GRUPPA_CODE
    DATE_BEG = config.get('Main', 'date_beg')
    DATE_END = config.get('Main', 'date_end')
    GRUPPA_CODE = config.get('Main', 'gruppa_code')

def read_query():
    with open(FILE_QRY, 'r', encoding='utf-8-sig') as f:
        str_qry = ''.join([s for s in f])
    str_qry = str_qry.replace('<DATE_BEG>', DATE_BEG)
    str_qry = str_qry.replace('<DATE_END>', DATE_END)
    str_qry = str_qry.replace('<GRUPPA_CODE>', GRUPPA_CODE)
    return str_qry

def exec_query(str_qry):
    with pyodbc.connect('DRIVER={SQL Server};SERVER=' + SERVER +
                        ';DATABASE=' + DATABASE +
                        ';UID=' + USERNAME +
                        ';PWD=' + PASSWORD) as conn:
        return pd.read_sql(str_qry, conn)

def graph(arr, mode):
    # строим график продаж по месяцам
    file_name = pathlib.Path(CURR_DIR, GRUPPA_CODE + mode + '.png')
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    sns.lineplot(data=arr, x='MONTH', y='SUMMA', hue='YEAR', palette='plasma')
    plt.grid(True)
    plt.title(f'Продажи, {mode}\n{GRUPPA_CODE}, {GRUPPA_NAME}')
    plt.xlabel('Месяц')
    plt.ylabel('Сумма')
    plt.savefig(file_name, dpi = 150)

def predict(arr, year, month):
    X = arr.query('MONTH == @month')
    y = X.loc[:, 'SUMMA'].values
    X = X.loc[:, 'YEAR'].values.reshape(-1, 1)
    model = RandomForestRegressor()
    model.fit(X, y)
    X_new = [[year]]
    return model.predict(X_new)[0]

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

def to_excel(arr):
    file_name = pathlib.Path(CURR_DIR, GRUPPA_CODE + 'прогноз.xls')
    arr.to_excel(file_name, columns=['YEAR', 'MONTH', 'SUMMA'], index=False)

read_ini()
str_qry = read_query()
arr = exec_query(str_qry)
GRUPPA_NAME = arr['GRUPPA_NAME'][0].strip()
graph(arr, 'факт')
arr = fill_array(arr)
graph(arr, 'прогноз')
to_excel(arr)

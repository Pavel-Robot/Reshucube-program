# -*- coding: utf-8 -*-

# Импортируем библиотеки
# Штатная библиотека для работы со временем
from datetime import datetime

# Собственно клиент для space-track
# Набор операторов для управления запросами. Отсюда нам понадобится время
import spacetrack.operators as op
# Главный класс для работы с space-track
from spacetrack import SpaceTrackClient
 

#функция для получения TLE в заданном диапазоне
# На вход идентификатор спутника, диапазон дат, имя пользователя и пароль.
def get_spacetrack_data(sat_id, start_date, end_date, username, password):

    # Реализуем экземпляр класса SpaceTrackClient, инициализируя его именем пользователя и паролем
    st = SpaceTrackClient(identity=username, password=password)
   
    # Выполнение запроса для диапазона дат:
    # Определяем диапазон дат через оператор библиотеки
    daterange = op.inclusive_range(start_date, end_date)
    
    # Выполняем запрос через st.tle
    data = st.tle(norad_cat_id=sat_id, orderby='epoch desc', format='tle', epoch = daterange)
    
    if not data:
        return 0, 0
 
    return data

#общая функция для получения данных и конвертирования строк в даты
def get_data_TLE(PATH, ID, start_date, end_date, username, password):
    
    ID = int(ID) #ID должно быть числом
    
    #переводим строки в нормальные даты, удаляем пробелы в строках
    start_date = datetime.strptime(str.lstrip((str.rstrip(start_date))), "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(str.lstrip((str.rstrip(end_date))), "%Y-%m-%d %H:%M:%S")
    
    #получаем данные TLE
    data = get_spacetrack_data(ID, start_date, end_date, username, password) 
    
    #Записываем в файл 
    name_of_file = str(ID)
    with open(PATH + '\\' + name_of_file + '.txt', 'w') as file:
        file.write(data)
    
    
















#импортируем библиотеки для работы с моделью SGP4
from sgp4.api import Satrec
from sgp4.api import SGP4_ERRORS

from sgp4.conveniences import sat_epoch_datetime  #sat_epoch_datetime(satellite) - возвращает эпоху

from astropy.coordinates import EarthLocation, AltAz #для вычисления положения относительно точки на Земле

from astropy.time import Time

from astropy.coordinates import TEME, CartesianDifferential, CartesianRepresentation
from astropy import units as u 

from astropy.coordinates import ITRS

# Штатная библиотека для работы со временем
from datetime import datetime, timedelta

#from datetime import timezone

import numpy as np
from numpy import abs

import pandas as pd
import matplotlib.pyplot as plt


#вход список с различными значениями, выход: индекс минимального значения и индекс максимального значения
def индекс(любой_список):
    Минимальный_индекс = любой_список.index(min(любой_список))
    Максимальный_индекс = любой_список.index(max(любой_список))
    
    return Минимальный_индекс, Максимальный_индекс



#вход - путь к файлу тле, выход - строки даты
def data_TLE_in_file(PATH_FILE_TLE):
    
    #получаем все TLE строки
    with open(PATH_FILE_TLE, "r") as file:
        data_TLE = file.readlines()

    #получаем список 1 и 2 строк TLE
    data_TLE1 = data_TLE[::2]
    data_TLE2 = data_TLE[1::2]
    
    return data_TLE1, data_TLE2
    

#вход: тле строки, выход: список эпох в юлианском виде 21344.63...
def get_TLE_epoch(data_TLE1, data_TLE2):
    
    список_эпох = []
    #Получаем метаданные из TLE
    for i in range(len(data_TLE1)):
    
        satellite = Satrec.twoline2rv(data_TLE1[i], data_TLE2[i]) #перерасчет метаданных TLE
    
        #получаем значение эпохи, то есть время в которое произошло обновление (корректировка) строк TLE
        эпоха = sat_epoch_datetime(satellite)
        эпоха = Time(эпоха, scale='utc')
        список_эпох.append(эпоха.jd)
    return список_эпох

#вход путь до файла тле, выход - мин и макс эпохи в файле
def узнать_эпохи(PATH_FILE_TLE):
    data_TLE1, data_TLE2 = data_TLE_in_file(PATH_FILE_TLE)
    список_эпох = get_TLE_epoch(data_TLE1, data_TLE2)
    Минимальная_эпоха_файла, Максимальная_эпоха_файла = индекс(список_эпох)
    Минимальная_эпоха = Time(список_эпох[Минимальная_эпоха_файла], format='jd')
    Максимальная_эпоха= Time(список_эпох[Максимальная_эпоха_файла], format='jd')

    return Минимальная_эпоха.datetime, Максимальная_эпоха.datetime




from mpl_toolkits.basemap import Basemap



def получить_данные(PATH_FILE_TLE, PATH_DIR, координаты_места, период_вычислений, время_начало, время_конец):
    
    #задаем положение (точку наблюдения) Красноярска относительно уровня моря ::: [долгота_места, широта_места, уровень_моря_в_метрах]
    siding_spring = EarthLocation.from_geodetic(координаты_места[0], координаты_места[1], координаты_места[2])
    
    #извлекаем из строки время, период между точками
    #время_периода = datetime.strptime(str.lstrip((str.rstrip(период_вычислений))), "%d:%H:%M:%S")
    время_периода = период_вычислений.replace(':',' ').split()
    время_периода = [int(i) for i in время_периода]
    период = timedelta(days = время_периода[0], hours = время_периода[1], minutes = время_периода[2], seconds = время_периода[3])
    период = период.total_seconds()
    
    #переводим строки в нормальные даты, удаляем пробелы в строках
    start_date = datetime.strptime(str.lstrip((str.rstrip(время_начало))), "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(str.lstrip((str.rstrip(время_конец))), "%Y-%m-%d %H:%M:%S")
    
    data_TLE1, data_TLE2 = data_TLE_in_file(PATH_FILE_TLE)
    список_эпох = get_TLE_epoch(data_TLE1, data_TLE2)

    #задаем нужные для нас списки в которые будут помещаться данные вычисленные внутри цикла while()

    список_времени = []

    список_уголместа = []
    список_азимута = []
    список_высот = []
    список_дистанция = []

    список_широты = []
    список_долготы = []

    список_координат_xyz = []
    список_скорости_xyz = []
    
    T = 0 #переменная для увеличения времени на промежуток времени 'период'
    while(True):

    
        #задаем начало и конец даты для вычислений положения
        t1 = Time(start_date+timedelta(seconds = T), scale='utc') #время расчетное
        t2 = Time(end_date, scale='utc')#конец
    
        

    
        #надо чтобы эпоха была ближе всех к расчетному времени
        #получаем эпоху по этому критерию. Отнимаем от эпохи расчетное время.
        список_разности = abs(np.array(список_эпох)-t1.jd).tolist() #используем numpy массивы, они намного быстрее, чем перебор списка
        мин_элемент = min(список_разности) #определяем, где меньше всего отличается эпоха
        индекс_списка = список_разности.index(мин_элемент)  #ищем индекс, где меньше всего отличается эпоха

    
        #определяем метаданные из TLE для самой актуальной эпохи
        satellite = Satrec.twoline2rv(data_TLE1[индекс_списка], data_TLE2[ индекс_списка])
    

        #print('Данные TLE. Актуальность эпохи TLE:',  sat_epoch_datetime(satellite)) #последнее обновление TLE, смотрим эпоху
        #print('Время определения положения по UTC:', t.datetime)
        #print()
    
        #получаем положение по 3м координатам xyz и скорость xyz в заданное время
        #error_code, положение, скорость = satellite.sgp4(t1.jd1, t1.jd2)  # in km and km/s
        #t.jd1 - значение год-месяц-день, а t.jd2 - час-мин-сек в юлианском формате даты
        #if error_code != 0:
        #    raise RuntimeError(SGP4_ERRORS[error_code])
        
        error_code, положение, скорость = satellite.sgp4(t1.jd1, t1.jd2)  # in km and km/s
        
        #Теперь, когда у нас есть положение и скорость в километрах и километрах в секунду,
        #мы можем создать положение в системе TEME отсчета:
        #положение и скорости спутника в декартовой системе координат
        teme_p = CartesianRepresentation(положение*u.km)
        teme_v = CartesianDifferential(скорость*u.km/u.s)


        #положение и скорости в абсолютной геоцентрической экваториальной системы координат (TEME)
        teme = TEME(teme_p.with_differentials(teme_v), obstime=t1)


        #когда координаты TEME известны, то становится возможным преобразование в другие системы координат
        # Переведем координаты спутника в экваториальную сферическую систему
        itrs = teme.transform_to(ITRS(obstime=t1))  
        location = itrs.earth_location
        loc = location.geodetic  
    
        #print(loc)
        #print(loc.lon)
        #print(loc.lat)
        #print(loc.height)

        #из определенного положения найти азимут, высоту и долготу
        #siding_spring = EarthLocation.of_site('aao')  
        aa = teme.transform_to(AltAz(obstime=t1, location=siding_spring))  

        #print(aa.alt.degree) 
        #print(aa.az.degree) 


        ###Возвращаемые данные:###
        #print('\nУгол места: ', aa.alt.degree)
        #print('Азимут: ', aa.az.degree)
        #print('Высота: ', loc.height)
        #print('Дистанция: ', aa.distance.km)
        #print('Широта: ', loc.lat.degree)
        #print('Долгота: ',loc.lon.degree)


        #print('Координаты x,y,z: ', teme_p)
        #print('Скорости x,y,z: ', teme_v)
    
    
        список_времени.append(t1.utc.datetime)

        список_уголместа.append(aa.alt.degree)
        список_азимута.append(aa.az.degree)
        список_высот.append(loc.height/u.km)
        список_дистанция.append(aa.distance.km)

        список_широты.append(loc.lat.degree)
        список_долготы.append(loc.lon.degree)
    
        список_координат_xyz.append(teme_p)
        список_скорости_xyz.append(teme_v)
    
        #задаем период между вычислениями
        T += период #секунды период между расчетами, 3600 сек = 1 часу
    
        if t1.jd >= t2.jd:
            break
    
    ###############
    #Строим графики#
    ###############

    fig, ax = plt.subplots()
    
    #fig.set_size_inches(10/2.54, 10/2.54) #задаем размеры (они в дюймах, но переводим в см)
    
    ax.plot(список_времени, список_высот, 'o') #scalex=False, scaley=False
    

    fig.autofmt_xdate() 
    #plt.xticks(rotation='vertical') 
    ax.grid(which='both')
    ax.set(title='Высота спутника над уровнем моря',  ylabel='Высота, км', xlabel='Время UTC')
    

    
    fig.savefig(PATH_DIR  + '\\' + 'спутник_высота.png', bbox_inches='tight')


    #########################
    #Сохраняем данные в файл#
    #########################

    #имя файла задаем
    name_excel_file = 'спутник.xlsx'

    #задаем название столбцов
    col = ['Дата', 'Высота, км', 'Угол места, град', 'Азимут, град', 'Дистанция от места на Земле, км', 'Широта, град',  'Долгота, град', 'список_координат_x, км', 'список_координат_y, км', 'список_координат_z, км', 'список_скорости_x, км/с','список_скорости_y, км/с','список_скорости_z, км/с']
    
    координаты_x = [i.x.value for i in список_координат_xyz]
    координаты_y = [i.y.value for i in список_координат_xyz]
    координаты_z = [i.z.value for i in список_координат_xyz]
    
    скорости_x = [i.d_x.value for i in список_скорости_xyz]
    скорости_y = [i.d_y.value for i in список_скорости_xyz]   
    скорости_z = [i.d_z.value for i in список_скорости_xyz]
    
    #пишем какие данные будут соответствовать ключу в словаре
    data = {'Дата': список_времени,
        'Высота, км': список_высот,
        'Угол места, град': список_уголместа,
        'Азимут, град': список_азимута,
        'Дистанция от места на Земле, км': список_дистанция,
        'Широта, град': список_широты,
        'Долгота, град':список_долготы,
        'список_координат_x, км':координаты_x,
        'список_координат_y, км':координаты_y,
        'список_координат_z, км':координаты_z,
        'список_скорости_x, км/с':скорости_x,
        'список_скорости_y, км/с':скорости_y,
        'список_скорости_z, км/с':скорости_z,
        }

    #создаем фрейм для дальнейшей записи
    frame = pd.DataFrame(data, columns=col)

    #записываем файл согласно формату:csv или excel
    frame.to_csv(PATH_DIR  + '\\' + 'спутник.csv', index=False, header=True)
    #frame.to_excel(PATH_DIR  + '\\' + name_excel_file, index=False)

    #вносим подстройки в документ excel для достойного отображения информации
    with pd.ExcelWriter(PATH_DIR  + '\\' + name_excel_file, engine='xlsxwriter') as wb:
        frame.to_excel(wb, sheet_name='Sheet1', index=False)
        sheet = wb.sheets['Sheet1'] #выбираем лист экселя
    
        #настраиваем ширину ячеек
        sheet.set_default_row(20) #определяем высоту для всех ячеек
        sheet.set_column(0, 14, 24) # Установить ширину одного столбцов от A=0 до 14.. в значение 30
        sheet.set_column(4, 4, 31) # Установить ширину одного столбцов от A=0 до 14.. в значение 30
        #.to_csv (r'C:\Users\Ron\Desktop\export_dataframe.csv', index = False, header=True)


    #############################################
    #Строим проекцию пути спутника на карте мира#
    #############################################


    

        
    fig = plt.figure(figsize=(12, 9))

    m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,\
                llcrnrlon=-180,urcrnrlon=180,resolution='c')
    #figsize(10,15)

     
    m.drawcoastlines()
    m.fillcontinents(color='coral',lake_color='aqua')

    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,20.), labels=[1,0,0,0], fontsize=14)
    m.drawmeridians(np.arange(-180.,181.,30.), labels=[0,0,0,1], fontsize=14)
    m.drawmapboundary(fill_color='aqua')
    #m.etopo() # карта светлая красивая
    #m.bluemarble() # карта голубая красивая
    #m.shadedrelief() #еще что то очень светлое

     
    m.scatter(список_долготы,список_широты, latlon=True,s=85,marker='o', color='red')
    #plt.title("Точки на карте мира", fontsize =14)
    
   # fig.savefig(PATH_DIR  + '\\' + 'спутник_gps.png', bbox_inches='tight')
   # plt.show()


    #подпись данных - тестовая функция https://www.easycoding.org/2016/12/17/postroenie-izolinij-na-karte-mira-pri-pomoshhi-python-basemap.html по контурам
    Flag = False
    if Flag == True:
        for i in range(0, len(список_высот), 1):
            plt.annotate(format(список_высот[i], '.1f'), xy=(список_долготы[i]+0.0, список_широты[i]), fontsize=8, color='pink')

    plt.savefig(PATH_DIR  + '\\' + 'спутник_gps.png', bbox_inches='tight')

    plt.show()




#считаем количество точек, чтобы регулировать их при рассчете и регулировать на графике
def количество_точек(время1, время2, период):
    
    #переводим строки в нормальные даты, удаляем пробелы в строках
    время1 = datetime.strptime(str.lstrip((str.rstrip(время1))), "%Y-%m-%d %H:%M:%S")
    время2 = datetime.strptime(str.lstrip((str.rstrip(время2))), "%Y-%m-%d %H:%M:%S")
    
    #извлекаем из строки время, период между точками
    время_периода = период.replace(':',' ').split()
    время_периода = [int(i) for i in время_периода]
    период = timedelta(days = время_периода[0], hours = время_периода[1], minutes = время_периода[2], seconds = время_периода[3])
    период = период.total_seconds()
    
    время = время2 - время1
    время = время.total_seconds()
    
    return время//период

import os
def open_help(): #открываем файл Как пользоваться.pdf
    path = 'help.pdf'
    os.system(path)







# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class Frame
###########################################################################

class Frame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Программа ReshUcube version=1.0.0", pos = wx.DefaultPosition, size = wx.Size( 548,494 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.menubar1 = wx.MenuBar( 0 )
        self.menu1 = wx.Menu()
        self.m_menuItem1 = wx.MenuItem( self.menu1, wx.ID_ANY, u"Открыть руководство", wx.EmptyString, wx.ITEM_NORMAL )
        self.menu1.Append( self.m_menuItem1 )

        self.menubar1.Append( self.menu1, u"Помощь" )

        self.SetMenuBar( self.menubar1 )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.panel1 = wx.Panel( self.notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_m1 = wx.BoxSizer( wx.VERTICAL )

        self.staticText1_m1 = wx.StaticText( self.panel1, wx.ID_ANY, u"Данный модуль позволяет производить скачивание данных TLE с сайта SpaceTrack.org", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.staticText1_m1.Wrap( -1 )

        bSizer_m1.Add( self.staticText1_m1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

        self.m1_textCtrl1 = wx.TextCtrl( self.panel1, wx.ID_ANY, u"Введите логин с сайта SpaceTrack", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m1.Add( self.m1_textCtrl1, 0, wx.ALL|wx.EXPAND, 5 )

        self.m1_textCtrl2 = wx.TextCtrl( self.panel1, wx.ID_ANY, u"Введите пароль с сайта SpaceTrack", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m1.Add( self.m1_textCtrl2, 0, wx.ALL|wx.EXPAND, 5 )

        self.m1_textCtrl3 = wx.TextCtrl( self.panel1, wx.ID_ANY, u"Введите id спутника TLE данные которого желаете получить. Пример ввода: 40427 ", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m1.Add( self.m1_textCtrl3, 0, wx.ALL|wx.EXPAND, 5 )

        self.m1_textCtrl4 = wx.TextCtrl( self.panel1, wx.ID_ANY, u"Введите начальную дату. Пример ввода: 2000-1-1 00:00:00", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m1.Add( self.m1_textCtrl4, 0, wx.ALL|wx.EXPAND, 5 )

        self.m1_textCtrl5 = wx.TextCtrl( self.panel1, wx.ID_ANY, u"Введите конечную дату. Пример ввода: 2020-1-1 00:00:00", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m1.Add( self.m1_textCtrl5, 0, wx.ALL|wx.EXPAND, 5 )

        self.m1_dirPicker1 = wx.DirPickerCtrl( self.panel1, wx.ID_ANY, u"Указать папку куда сохранить файл .txt с данными TLE спутника", u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
        bSizer_m1.Add( self.m1_dirPicker1, 0, wx.ALL|wx.EXPAND, 5 )

        self.m1_button1 = wx.Button( self.panel1, wx.ID_ANY, u"Получить данные", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m1.Add( self.m1_button1, 0, wx.ALL|wx.EXPAND, 5 )

        self.m1_pictireSIBGU = wx.StaticBitmap( self.panel1, wx.ID_ANY, wx.Bitmap( u"Полное_интро.jpg", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m1.Add( self.m1_pictireSIBGU, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )


        self.panel1.SetSizer( bSizer_m1 )
        self.panel1.Layout()
        bSizer_m1.Fit( self.panel1 )
        self.notebook1.AddPage( self.panel1, u"Модуль 1", True )
        self.m_panel7 = wx.Panel( self.notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer_m2 = wx.BoxSizer( wx.VERTICAL )

        self.m2_staticText1 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Данный модуль позволяет рассчитать высоту спутника на орбите в определенный момент времени\n", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
        self.m2_staticText1.Wrap( -1 )

        bSizer_m2.Add( self.m2_staticText1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

        self.m2_filePicker1 = wx.FilePickerCtrl( self.m_panel7, wx.ID_ANY, u"Выберите файл .txt с данными TLE в обозревателе", u"Select a file", u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
        bSizer_m2.Add( self.m2_filePicker1, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_textCtrl1 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"Максимальная эпоха TLE спутника. Выберите файл .txt с данными TLE в обозревателе.", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_textCtrl1, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_textCtrl2 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"Минимальная эпоха TLE спутника. Выберите файл .txt с данными TLE в обозревателе", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_textCtrl2, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_textCtrl3 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"Напишите точку наблюдения. Пример ввода координат Красноярска: 93.0491, 56.029, 287", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_textCtrl3, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_textCtrl4 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"Введите начальную дату. Пример ввода: 2000-1-1 00:00:00", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_textCtrl4, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_textCtrl5 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"Введите конечную дату. Пример ввода: 2020-1-1 00:00:00", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_textCtrl5, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_textCtrl6 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"Введите период между точками. Пример ввода: 0:00:00:00", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_textCtrl6, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_textCtrl7 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"Здесь ведется расчет количества точек (зависит от начальной и конечной даты, и периода).", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_textCtrl7, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_dirPicker2 = wx.DirPickerCtrl( self.m_panel7, wx.ID_ANY, u"Выберите папку для сохранения графиков и excel файла с данными.", u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
        bSizer_m2.Add( self.m2_dirPicker2, 0, wx.ALL|wx.EXPAND, 5 )

        self.m2_button1 = wx.Button( self.m_panel7, wx.ID_ANY, u"Выполнить программу", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer_m2.Add( self.m2_button1, 0, wx.ALL|wx.EXPAND, 5 )


        self.m_panel7.SetSizer( bSizer_m2 )
        self.m_panel7.Layout()
        bSizer_m2.Fit( self.m_panel7 )
        self.notebook1.AddPage( self.m_panel7, u"Модуль 2", False )

        bSizer1.Add( self.notebook1, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

		# Connect Events
        self.Bind( wx.EVT_MENU, self.help, id = self.m_menuItem1.GetId() )
        self.m1_textCtrl1.Bind( wx.EVT_TEXT, self.m1_login_spacetrack )
        self.m1_textCtrl2.Bind( wx.EVT_TEXT, self.m1_password_spacetrack )
        self.m1_textCtrl3.Bind( wx.EVT_TEXT, self.m1_id_sat )
        self.m1_textCtrl4.Bind( wx.EVT_TEXT, self.m1_time1 )
        self.m1_textCtrl5.Bind( wx.EVT_TEXT, self.m1_time2 )
        self.m1_dirPicker1.Bind( wx.EVT_DIRPICKER_CHANGED, self.m1_dir_path )
        self.m1_button1.Bind( wx.EVT_BUTTON, self.m1_but1 )
        
        self.m2_filePicker1.Bind( wx.EVT_FILEPICKER_CHANGED, self.m2_dirFile1 )
        self.m2_textCtrl1.Bind( wx.EVT_TEXT, self.m2_max_tle )
        self.m2_textCtrl2.Bind( wx.EVT_TEXT, self.m2_min_tle )
        self.m2_textCtrl3.Bind( wx.EVT_TEXT, self.m2_point_of_look )
        self.m2_textCtrl4.Bind( wx.EVT_TEXT, self.m2_start_date )
        self.m2_textCtrl5.Bind( wx.EVT_TEXT, self.m2_end_date )
        self.m2_textCtrl6.Bind( wx.EVT_TEXT, self.m2_period )
        self.m2_textCtrl7.Bind( wx.EVT_TEXT, self.m2_points )
        self.m2_dirPicker2.Bind( wx.EVT_DIRPICKER_CHANGED, self.m2_dirPath1 )
        self.m2_button1.Bind( wx.EVT_BUTTON, self.m2_but1 )

    def __del__( self ):
        pass


	# Virtual event handlers, override them in your derived class
    def help( self, event ):
        print('Открываю файл помощи!')
        open_help()
    #Вкладка модуль1
    def m1_login_spacetrack( self, event ):
        global login
        login = self.m1_textCtrl1.GetValue()

    def m1_password_spacetrack( self, event ):
        global password
        password = self.m1_textCtrl2.GetValue()        

    def m1_id_sat( self, event ):
        global id_sat
        id_sat = self.m1_textCtrl3.GetValue()  

    def m1_time1( self, event ):
        global m1_time1
        m1_time1 = self.m1_textCtrl4.GetValue()  

    def m1_time2( self, event ):
        global m1_time2
        m1_time2 = self.m1_textCtrl5.GetValue()  

    def m1_dir_path( self, event ):
        global m1_dir_path
        m1_dir_path = self.m1_dirPicker1.GetPath()

    def m1_but1( self, event ):
        print("Начало работы модуля 1...")
        get_data_TLE(m1_dir_path, id_sat, m1_time1, m1_time2, login, password)
        print("Модуль 1 успешно завершил работу!")
        
    #Вкладка модуль2
    def m2_dirFile1( self, event ):
        global m2_dirFile1
        m2_dirFile1 = self.m2_filePicker1.GetPath()
        
        
        global m2_max_tle, m2_min_tle
        
        print('Определяю эпохи...')
        m2_max_tle, m2_min_tle = узнать_эпохи(m2_dirFile1)
        print('Определяю эпохи.. готово.')
        
        self.m2_textCtrl1.SetValue(str(m2_max_tle)) 
        self.m2_textCtrl2.SetValue(str(m2_min_tle)) 

    def m2_max_tle( self, event ):
        event.Skip()

    def m2_min_tle( self, event ):
        event.Skip()

    def m2_point_of_look( self, event ): #положение наблюдение на Земле
        global point_look
        point_look = self.m2_textCtrl3.GetValue()
        point_look = point_look.replace(',','').split()

    def m2_start_date( self, event ):
        global m2_start_date
        m2_start_date = self.m2_textCtrl4.GetValue()

    def m2_end_date( self, event ):
        global m2_end_date
        m2_end_date = self.m2_textCtrl5.GetValue()

    def m2_period( self, event ):
        global m2_period
        m2_period = self.m2_textCtrl6.GetValue()
        
        print('Определяю количество точек...')
        кол_точек = количество_точек(m2_start_date, m2_end_date, m2_period)
        print('Определяю количество точек.. готово.')
        
        self.m2_textCtrl7.SetValue(str(кол_точек)) 

    def m2_points( self, event ):
        event.Skip()

    def m2_dirPath1( self, event ):
        global m2_dirPath1
        m2_dirPath1 = self.m2_dirPicker2.GetPath()
    

    def m2_but1( self, event ):
        print('Выполняю модуль 2...')
        получить_данные(m2_dirFile1, m2_dirPath1, point_look, m2_period, m2_start_date, m2_end_date)
        print('Выполняю модуль 2.. готово.')







if __name__ == '__main__':
    app = wx.App(False)
    frame = Frame(None)
    

    
    frame.Show()
    #print("text = ", frame.Teeeext(None)) #работает только если функция возвращает значение
    
    app.MainLoop()
    #print(global_Text)
    

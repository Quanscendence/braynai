from coreapp.models import *
from datetime import datetime, date, timedelta
from django.contrib.auth.models import Group, User, Permission
import pytz

india_timezone = pytz.timezone('Asia/Kolkata')
#india_timezone.localize(datetime.strptime('Sep 1 2017  12:01AM', '%b %d %Y %I:%M%p'))


def addData():
    #delete all the type
    # delete = IndustryChoices.objects.all().delete()
    #create industries types
    industries_list = ['BEAUTY AND FITNESS',
            'FISHING'
            'SHIPPING ',
            'PRINTING AND PUBLISHING',
            'FASHION',
            'BIOTECHNOLOGY',
            'INFRASTRUCTURE',
            'LOGISTICS',
            'RESORTS',
            'TRAVEL',
            'SPORTS',
            'SHOPPING',
            'PETS AND ANIMALS',
            'PEOPLE AND SOCIETY',
            'ONLINE COMMUNITIES',
            'LAW AND GOVERNMENT',
            'JOBS AND EDUCATION',
            'HOME AND GARDEN',
            'HOBBIES AND LEISURE',
            'GAMES',
            'BOOKS AND LITERATURE',
            'TOURISM AND HOSPITALITY',
            'TEXTILES',
            'TELECOMMUNICATIONS',
            'INDIAN SERVICES INDUSTRY ',
            'SCIENCE AND TECHNOLOGY',
            'ROADS',
            'RETAIL',
            'RENEWABLE ENERGY',
            'REAL ESTATE',
            'RAILWAYS'
            'POWER',
            'PORTS',
            'PHARMACEUTICALS',
            'OIL AND GAS',
            'METALS AND MINING',
            'MEDIA AND ENTERTAINMENT',
            'MANUFACTURING',
            'IT & ITES',
            'INSURANCE',
            'GEMS AND JEWELLERY',
            'FMCG',
            'FINANCIAL SERVICES',
            'ENGINEERING AND CAPITAL GOODS',
            'EDUCATION AND TRAINING',
            'ECOMMERCE',
            'CONSUMER DURABLES',
            'BANKING',
            'AVIATION',
            'AUTOMOBILES',
            'AGRICULTURE AND ALLIED INDUSTRIES',
            'HEALTHCARE']
    for type in industries_list:
        industries, created = IndustryChoices.objects.get_or_create(name=type)
    print('creates')
def run():

    addData()

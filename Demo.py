import requests
from bs4 import BeautifulSoup
import time

# url:台鐵網站 時間預設今日 00:00-23:59
url = 'https://www.railway.gov.tw/tra-tip-web/tip'
staDic = {}
searchDay = time.strftime('%Y/%m/%d')
sTime = '00:00'
eTime = '23:59'


def getTrip(searchDay, startStation, endStation, sTime, eTime):
    resp = requests.get(url)
    if resp.status_code != 200:
        print('URL發生錯誤:' + url)
        return

    soup = BeautifulSoup(resp.text, 'html.parser')
    stations = soup.find(id='cityHot').ul.find_all('li')
    for station in stations:
        stationName = station.button.text
        stationId = station.button['title']
        staDic[stationName] = stationId

    csrf = soup.find(id='queryForm').find('input', {'name': '_csrf'})['value']
    formData = {
        'trainTypeList': 'ALL',
        'transfer': 'ONE',
        'startOrEndTime': 'true',
        'startStation': staDic[startStation],
        'endStation': staDic[endStation],
        'rideDate': searchDay,
        'startTime': sTime,
        'endTime': eTime
    }

    queryUrl = soup.find(id='queryForm')['action']
    # print('queryUrl-%s' % queryUrl)
    # print('formData-%s' % formData)
    qResp = requests.post('https://www.railway.gov.tw' + queryUrl, data=formData)
    # print(qResp.status_code)
    qSoup = BeautifulSoup(qResp.text, 'html.parser')
    trs = qSoup.find_all('tr', 'trip-column')
    # print(len(trs))
    print('車種車號: (發車/抵達)時間, 所需車程')
    for tr in trs:
        td = tr.find_all('td')
        print('%s : %s----%s, %s' % (td[0].ul.li.a.text, td[1].text, td[2].text, td[3].text))


# 轉換單字  台 轉成 臺
def transTraditionChar(stationName):
    if "台" in stationName:
        stationName = stationName.replace("台", "臺")
    return stationName


checkToday = input(f'是否查詢今日{searchDay}車班:(Y/N)')
if checkToday.lower() != "y":
    checkToday = input(f'請填入查詢日期(格式:yyyy/mm/dd)')

print('以下請依此時間格式(hh:mm)(24小時制)填入')
startTime = input('查詢開始時間:')
endTime = input('查詢結束時間:')

startStation = input('查詢起點站名:')
startStation = transTraditionChar(startStation)
endStation = input('查詢終點站名:')
endStation = transTraditionChar(endStation)

getTrip(searchDay, startStation, endStation, startTime, endTime)

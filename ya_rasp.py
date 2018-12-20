# -*- coding: utf-8 -*-

import requests
import datetime
import matplotlib.pyplot as plt


datetime_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(seconds=10800), 'MSK'))


def request_schedule():
    apikey = open('apikey.txt', 'r').readline()

    PARAMS_TO_MSK = {'apikey': apikey,
                     'limit': '600',
                     'station': 's9600701',
                     'date': datetime_msk.date().isoformat(),
                     'transport_types': 'suburban',
                     'direction': 'на Москву'}

    PARAMS_FROM_MSK = {'apikey': apikey,
                       'limit': '600',
                       'station': 's9600701',
                       'date': datetime_msk.date().isoformat(),
                       'transport_types': 'suburban',
                       'direction': 'на Александров'}

    URL = 'https://api.rasp.yandex.net/v3.0/schedule/'

    try:
        response_to_msk = requests.get(URL, PARAMS_TO_MSK)
        response_to_msk.raise_for_status()

        response_from_msk = requests.get(URL, PARAMS_FROM_MSK)
        response_from_msk.raise_for_status()
    except BaseException as e:
        print(e)
        exit(1)

    schedule_to_msk = response_to_msk.json()
    schedule_from_msk = response_from_msk.json()

    return schedule_to_msk, schedule_from_msk


def calc_closed_crossing_datetimes(schedule_to_msk, schedule_from_msk):

    closed_crossing_datetimes = set()  # время закрытого переезда

    # добавление времени электричек на москву
    offset_minutes_to_msk = 9

    for sch_row in schedule_to_msk['schedule']:
        if sch_row['thread']['title'] == 'Пушкино — Москва (Ярославский вокзал)':
            continue
        dt = datetime.datetime.fromisoformat(sch_row['arrival'])
        dt = dt - datetime.timedelta(minutes=offset_minutes_to_msk)
        closed_crossing_datetimes.add(dt)

    # добавление времени электричек из москвы
    offset_minutes_from_msk = 5

    for sch_row in schedule_from_msk['schedule']:
        if sch_row['thread']['title'] == 'Москва (Ярославский вокзал) — Пушкино':
            continue
        dt = datetime.datetime.fromisoformat(sch_row['departure'])
        dt = dt + datetime.timedelta(minutes=offset_minutes_from_msk)
        closed_crossing_datetimes.add(dt)

    closed_crossing_datetimes = list(closed_crossing_datetimes)
    closed_crossing_datetimes.sort()
    return closed_crossing_datetimes


def pretty_print(closed_crossing_datetimes):
    index_divider_current_dt = 0
    for i, dt in enumerate(closed_crossing_datetimes):
        if dt > datetime_msk:
            index_divider_current_dt = i
            break

    for i in range(index_divider_current_dt):
        hh, mm = closed_crossing_datetimes[i].hour, closed_crossing_datetimes[i].minute
        print('{:02d}:{:02d}'.format(hh, mm))

    print('<-- now {:02d}:{:02d}'.format(datetime_msk.hour, datetime_msk.minute))

    for i in range(index_divider_current_dt, len(closed_crossing_datetimes)):
        hh, mm = closed_crossing_datetimes[i].hour, closed_crossing_datetimes[i].minute
        print('{:02d}:{:02d}'.format(hh, mm))


if __name__ == '__main__':
    sch_to_msk, sch_from_msk = request_schedule()
    closed_dts = calc_closed_crossing_datetimes(sch_to_msk, sch_from_msk)
    pretty_print(closed_dts)

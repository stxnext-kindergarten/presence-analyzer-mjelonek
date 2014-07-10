# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import locale
from json import dumps
from functools import wraps
from datetime import datetime
from urllib import urlopen
from threading import Lock

from flask import Response
from lxml import etree

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=C0103

CACHE = {}
LOCK = Lock()


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        Returns a response.
        """
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


def cache(seconds):
    """
    Caches the return content of a function.
    """
    def decorator(function):
        def inner():
            global CACHE
            if not CACHE or (datetime.now() - CACHE['time']).seconds > seconds:
                CACHE = {
                    'time': datetime.now(),
                    'data': function(),
                }
            return CACHE['data']
        return inner
    return decorator


def lock(function):
    """
    Locks function.
    """
    def inner():
        with LOCK:
            return function()
    return inner


@lock
@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}
    return data


def get_xml_data():
    """
    Extracts user data from XML file.
    """
    data = {}
    with open(app.config['DATA_XML'], 'r') as xmlfile:
        tree = etree.parse(xmlfile)
        host = tree.findtext('./server/host')
        protocol = tree.findtext('./server/protocol')
        url = '{0}://{1}'.format(protocol, host)

        users = tree.findall('./users/user')
        locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')
        users.sort(key=lambda k: k.findtext('name'), cmp=locale.strcoll)
        locale.setlocale(locale.LC_ALL, (None, None))

        data = [{
            'id': int(user.get('id')),
            'name': user.findtext('name'),
            'avatar': '{0}{1}'.format(url, user.findtext('avatar')),
        } for user in users]

    return data


def update_xml_data():
    """
    Updates local xml file with newest one.
    """
    with open('runtime/data/sample_xml_data.xml', 'wb') as xmlfile:
        xmlfile.write(urlopen('http://sargo.bolt.stxnext.pl/users.xml').read())


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_start_end_by_weekday(items):
    """
    Groups start-end entries by weekday.
    """
    result = {i: {'start': [], 'end': []} for i in range(7)}
    for date in items:
        start = seconds_since_midnight(items[date]['start'])
        end = seconds_since_midnight(items[date]['end'])
        result[date.weekday()]['start'].append(start)
        result[date.weekday()]['end'].append(end)
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0

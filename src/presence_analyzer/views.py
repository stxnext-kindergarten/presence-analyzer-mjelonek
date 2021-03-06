# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, abort
from flask.ext.mako import render_template
from mako.exceptions import TopLevelLookupException

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_start_end_by_weekday,
    get_xml_data
)

import logging
log = logging.getLogger(__name__)  # pylint: disable=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect("presence_weekday.html")


@app.route('/<site>')
def presence_page(site=None):
    """
    Returns rendered site.
    """
    try:
        return render_template(site)
    except TopLevelLookupException:
        abort(404)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v2/users')
@jsonify
def users_xml_view():
    """
    Users with name, avatar listing.
    """
    return get_xml_data()


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns start, end time when user is most often present grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_start_end_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday],
         mean(start_end_dict['start']),
         mean(start_end_dict['end']))
        for weekday, start_end_dict in weekdays.items()
    ]
    return result

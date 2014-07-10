# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'runtime',
    'data',
    'test_data.csv'
)

TEST_DATA_CSV_CACHE = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'runtime',
    'data',
    'test_data_cache.csv'
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'runtime',
    'data',
    'test_xml_data.xml'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_presence_start_end_page(self):
        """
        Test presence start-end page.
        """
        resp = self.client.get('/presence_start_end.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')
        self.assertIn('Timeline', resp.data)
        self.assertIn('<li id="selected">\n                    '
                      '<a href="/presence_start_end.html">',
                      resp.data)

    def test_presence_weekday_page(self):
        """
        Test presence weekday page.
        """
        resp = self.client.get('/presence_weekday.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')
        self.assertIn('PieChart', resp.data)
        self.assertIn('<li id="selected">\n                    '
                      '<a href="/presence_weekday.html">',
                      resp.data)

    def test_presence_mean_time_page(self):
        """
        Test presence mean time page.
        """
        resp = self.client.get('/mean_time_weekday.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')
        self.assertIn('ColumnChart', resp.data)
        self.assertIn('<li id="selected">\n                    '
                      '<a href="/mean_time_weekday.html">',
                      resp.data)

    def test_not_found_page(self):
        """
        Test 404 not found page.
        """
        resp = self.client.get('/this_site_doesnt_exist.html')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')
        self.assertIn('404 Not Found', resp.data)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_xml_users(self):
        """
        Test xml users listing.
        """
        resp = self.client.get('/api/v2/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        sample_data = [
            {
                u'id':  141,
                u'name': u'Adam P.',
                u'avatar': u'https://intranet.stxnext.pl/api/images/users/141',
            },
            {
                u'id': 176,
                u'name': u'Adrian K.',
                u'avatar': u'https://intranet.stxnext.pl/api/images/users/176',
            },
        ]
        self.assertEqual(data, sample_data)

    def test_api_mean_time_weekday(self):
        """
        Test mean user time grouped by weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/5')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])

        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        correct_data = [
            [u'Mon', 0],
            [u'Tue', 30047],
            [u'Wed', 24465],
            [u'Thu', 23705],
            [u'Fri', 0],
            [u'Sat', 0],
            [u'Sun', 0],
        ]
        self.assertEqual(data, correct_data)

    def test_api_presence_weekday_view(self):
        """
        Test total user presence time grouped by weekday.
        """
        resp = self.client.get('/api/v1/presence_weekday/5')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])

        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        correct_data = [
            [u'Weekday', u'Presence (s)'],
            [u'Mon', 0],
            [u'Tue', 30047],
            [u'Wed', 24465],
            [u'Thu', 23705],
            [u'Fri', 0],
            [u'Sat', 0],
            [u'Sun', 0],
        ]
        self.assertEqual(data, correct_data)

    def test_api_presence_start_end(self):
        """
        Test time intervals when user is most often present grouped by weekday.
        """
        resp = self.client.get('/api/v1/presence_start_end/5')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])

        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        correct_data = [
            [u'Mon', 0, 0],
            [u'Tue', 34745, 64792],
            [u'Wed', 33592, 58057],
            [u'Thu', 38926, 62631],
            [u'Fri', 0, 0],
            [u'Sat', 0, 0],
            [u'Sun', 0, 0],
        ]
        self.assertEqual(data, correct_data)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_get_data_cache(self):
        """
        Test caching data.
        """
        data = utils.get_data()
        self.assertDictEqual(utils.CACHE['data'], data)

        main.app.config.update({'DATA_CSV': TEST_DATA_CSV_CACHE})
        data = utils.get_data()
        self.assertDictEqual(utils.CACHE['data'], data)

        utils.CACHE = {}
        data = utils.get_data()
        self.assertDictEqual(utils.CACHE['data'], data)

        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        utils.CACHE = {}

    def test_get_xml_data(self):
        """
        Test parsing XML file.
        """
        data = utils.get_xml_data()
        self.assertIsInstance(data, list)
        sample_avatar = 'https://intranet.stxnext.pl/api/images/users/141'
        self.assertEqual(sample_avatar, data[0]['avatar'])
        sample_name = 'Adam P.'
        self.assertEqual(sample_name, data[0]['name'])

    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight.
        """
        seconds = utils.seconds_since_midnight(datetime.time(1, 0, 15))
        self.assertEqual(seconds, 3615)

    def test_interval(self):
        """
        Test interval between two datetime.time objects
        """
        interval = utils.interval(
            datetime.time(1, 0, 15),
            datetime.time(3, 30, 27)
        )
        self.assertEqual(interval, 9012)

    def test_mean(self):
        """
        Test arithmetic mean from list
        """
        mean = utils.mean([])
        self.assertEqual(mean, 0)
        mean = utils.mean([1, 2, 3, 4])
        self.assertEqual(mean, 2.5)
        mean = utils.mean([-1, -2, -3, -4])
        self.assertEqual(mean, -2.5)
        mean = utils.mean([0.5, 1.25, 1.5, 2.13])
        self.assertAlmostEqual(mean, 1.345)
        mean = utils.mean([1.237, -3.23, -1.775])
        self.assertAlmostEqual(mean, -1.256)
        mean = utils.mean([5.234, -2.34, 1.113, 3.2412, -0.1853, 0.54, 0.797])
        self.assertAlmostEqual(mean, 1.1999857)

    def test_group_by_weekday(self):
        """
        Test presence entries grouped by weekday.
        """
        user_id = utils.get_data()[10]
        result = utils.group_by_weekday(user_id)
        data = {
            0: [],
            1: [30047],
            2: [24465],
            3: [23705],
            4: [],
            5: [],
            6: [],
        }
        self.assertDictEqual(result, data)

    def test_group_start_end_by_weekday(self):
        """
        Test start, end presence entries grouped by weekday.
        """
        user_id = utils.get_data()[10]
        result = utils.group_start_end_by_weekday(user_id)
        data = {
            0: {'start': [], 'end': []},
            1: {'start': [34745], 'end': [64792]},
            2: {'start': [33592], 'end': [58057]},
            3: {'start': [38926], 'end': [62631]},
            4: {'start': [], 'end': []},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []},
        }
        self.assertDictEqual(result, data)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()

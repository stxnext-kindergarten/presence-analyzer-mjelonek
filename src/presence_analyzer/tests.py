# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest
import calendar

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
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
        self.assertEqual(data[0], [u'Mon', 0])
        self.assertEqual(data[1], [u'Tue', 30047])
        self.assertEqual(data[2], [u'Wed', 24465])
        self.assertEqual(data[3], [u'Thu', 23705])
        self.assertEqual(data[4], [u'Fri', 0])
        self.assertEqual(data[5], [u'Sat', 0])
        self.assertEqual(data[6], [u'Sun', 0])

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
        self.assertEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertEqual(data[1], [u'Mon', 0])
        self.assertEqual(data[2], [u'Tue', 30047])
        self.assertEqual(data[3], [u'Wed', 24465])
        self.assertEqual(data[4], [u'Thu', 23705])
        self.assertEqual(data[5], [u'Fri', 0])
        self.assertEqual(data[6], [u'Sat', 0])
        self.assertEqual(data[7], [u'Sun', 0])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

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
        interval = utils.interval(datetime.time(1, 0, 15),
                                  datetime.time(3, 30, 27))
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

    def test_group_by_weekday(self):
        """
        Test presence entriers grouped by weekday.
        """
        user_id = {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(11, 0, 0),
                'end': datetime.time(13, 30, 0),
            },
            datetime.date(2013, 10, 5): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
        result = utils.group_by_weekday(user_id)
        data = {i: [] for i in range(7)}
        data[1] = [30600]
        data[2] = [9000]
        data[5] = [29700]
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

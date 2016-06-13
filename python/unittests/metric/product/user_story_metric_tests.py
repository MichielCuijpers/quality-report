"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest

from qualitylib import metric, domain, metric_source


class FakeBirt(object):
    """ Provide for a fake Birt object. """

    def __init__(self):
        self.down = False

    @staticmethod
    def approved_user_stories(birt_id):  # pylint: disable=unused-argument
        """ Return the number of approved user stories. """
        return 20

    def reviewed_user_stories(self, birt_id):  # pylint: disable=unused-argument
        """ Return the number of reviewed user stories. """
        return -1 if self.down else 23

    def nr_user_stories(self, birt_id):  # pylint: disable=unused-argument
        """ Return the total number of user stories. """
        return -1 if self.down else 25

    @staticmethod
    def nr_user_stories_with_sufficient_ltcs(birt_id):  # pylint: disable=unused-argument
        """ Return the number of user stories with enough logical test cases. """
        return 23

    @staticmethod
    def whats_missing_url(product):  # pylint: disable=unused-argument
        """ Return the url for the what's missing report. """
        return 'http://whats_missing'


class FakeSubject(object):
    """ Provide for a fake subject. """
    version = ''

    def __init__(self, birt_id=True):
        self.__birt_id = birt_id

    @staticmethod
    def name():
        """ Return the name of the subject. """
        return 'FakeSubject'

    def metric_source_id(self, metric_scr):  # pylint: disable=unused-argument
        """ Return the metric source id of the subject for the metric source. """
        return 'birt id' if self.__birt_id else ''

    def product_version(self):
        """ Return the product version. """
        return self.version

    @staticmethod
    def required_metric_classes():
        """ Return a list of reuired metric classes. """
        return [metric.UserStoriesNotReviewed, metric.UserStoriesNotApproved,
                metric.UserStoriesWithTooFewLogicalTestCases]


class UserStoriesNotReviewedTest(unittest.TestCase):
    """ Unit tests for the user stories that are not reviewed. """
    def setUp(self):
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.UserStoriesNotReviewed(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not reviewed user stories as reported by Birt. """
        self.assertEqual(2, self.__metric.value())

    def test_value_on_error(self):
        """ Test that the value is -1 when the metric source is down. """
        self.__birt.down = True
        self.assertEqual(-1, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject heeft 2 niet gereviewde user stories van in totaal 25 user stories.',
                         self.__metric.report())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())

    def test_will_be_measured_for_trunk_product(self):
        """ Test that the metric will be measured for trunk versions. """
        self.assertTrue(metric.UserStoriesNotReviewed.should_be_measured(self.__subject))

    def test_wont_be_measured_for_released_product(self):
        """ Test that the metric can only be measured for trunk versions. """
        product = self.__subject
        product.version = '1.1'
        self.assertFalse(metric.UserStoriesNotReviewed.should_be_measured(product))


class UserStoriesNotApprovedTest(unittest.TestCase):
    """ Unit tests for the user stories that are not approved. """
    def setUp(self):
        birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: birt})
        self.__metric = metric.UserStoriesNotApproved(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of not approved user stories as reported by Birt. """
        self.assertEqual(3, self.__metric.value())

    def test_report(self):
        """ Test that the report is correct. """
        self.assertEqual('FakeSubject heeft 3 niet goedgekeurde user stories van in totaal 23 gereviewde user stories.',
                         self.__metric.report())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual({'Birt': 'http://whats_missing'}, self.__metric.url())

    def test_will_be_measured_for_trunk_product(self):
        """ Test that the metric will be measured for trunk version. """
        self.assertTrue(metric.UserStoriesNotApproved.should_be_measured(self.__subject))

    def test_wont_be_measured_for_released_product(self):
        """ Test that the metric can only be measured for trunk versions. """
        product = self.__subject
        product.version = '1.1'
        self.assertFalse(metric.UserStoriesNotApproved.should_be_measured(product))


class UserStoriesWithEnoughLTCsTest(unittest.TestCase):
    """ Unit tests for the user-stories-with-enough-logical-test-cases-metric. """
    def setUp(self):
        self.__birt = FakeBirt()
        self.__subject = FakeSubject()
        self.__project = domain.Project(metric_sources={metric_source.Birt: self.__birt})
        self.__metric = metric.UserStoriesWithTooFewLogicalTestCases(subject=self.__subject, project=self.__project)

    def test_value(self):
        """ Test that the value of the metric is the number of user stories that has too few logical test cases
            as reported by Birt. """
        self.assertEqual(2, self.__metric.value())

    def test_url(self):
        """ Test the url is correct. """
        self.assertEqual(dict(Birt=self.__birt.whats_missing_url('product')), self.__metric.url())

    def test_will_be_measured_for_trunk_product(self):
        """ Test that the metric will be measured for trunk version. """
        self.assertTrue(metric.UserStoriesWithTooFewLogicalTestCases.should_be_measured(self.__subject))

    def test_wont_be_measured_for_released_product(self):
        """ Test that the metric will only be measured for trunk versions. """
        product = self.__subject
        product.version = '1.1'
        self.assertFalse(metric.UserStoriesWithTooFewLogicalTestCases.should_be_measured(product))

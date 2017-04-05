"""
Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid

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


import functools
import logging
import urllib

from . import url_opener
from .. import utils, domain


class Checkmarx(domain.MetricSource):
    """ Class representing the Checkmarx API. """
    metric_source_name = 'Checkmarx'
    needs_metric_source_id = True
    checkmarx_url = ''
    report_url = ''

    def __init__(self, url, username, password, url_open=None, **kwargs):
        self._url_open = url_open or url_opener.UrlOpener("", username, password)
        self.checkmarx_url = url
        self.report_url = "{}/CxWebClient/".format(url)
        super().__init__()

    def metric_source_urls(self, *report_urls):
        for project_name in report_urls:
            logging.warning("project_name %s", project_name)
            return self.report_url

    #@functools.lru_cache(maxsize=1024)
    def alerts(self, risk_level, *report_urls):
        """ Return the number of alerts of the specified risk level. """
        nr_alerts = 0
        for project_name in report_urls:
            try:
                json = self.__fetch_report(project_name)
                nr_alerts += self.__parse_alerts(json, risk_level)
                self.report_url = "{}/CxWebClient/ViewerMain.aspx?scanId={}&ProjectID={}"\
                    .format(self.checkmarx_url, str(json["value"][0]["LastScan"]["Id"]), str(json["value"][0]["LastScan"]["ProjectId"]))
            #except url_opener.UrlOpener.url_open_exceptions:
            #    return -1
            except Exception as reason:
                logging.warning("Couldn't parse alerts with %s risk level from %s - %s", risk_level, self.checkmarx_url, reason)
                return -1
        return nr_alerts

    @staticmethod
    def __parse_alerts(json, risk_level):
        """ Parse the JSON to get the nr of alerts for the risk_level """

        return json["value"][0]["LastScan"][risk_level.title()]

    def __fetch_report(self, project_name):
        api_url = "{}/Cxwebinterface/odata/v1/Projects?$expand=LastScan" \
                  "&$filter=LastScan/Results/any(r:%20r%2fSeverity%20eq%20CxDataRepository.Severity%27High%27" \
                  "%20or%20r%2fSeverity%20eq%20CxDataRepository.Severity%27Medium%27%29%20and%20Name%20eq%20%27{}%27"\
            .format(self.checkmarx_url, project_name)

        logging.debug("api_url: %s", api_url)
        json = self.__get_json(api_url)
        return json

    def __get_json(self, api_url):
        """ Return and evaluate the JSON at the url using Basic Authentication. """

        try:
            import ssl

            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                # Legacy Python that doesn't verify HTTPS certificates by default
                pass
            else:
                # Handle target environment that doesn't support HTTPS verification
                ssl._create_default_https_context = _create_unverified_https_context

            json_string = self._url_open.url_read(api_url)
        except Exception as reason:
            logging.warning("Couldn't open %s: %s", api_url, reason)
            raise

        json = utils.eval_json(json_string)
        return json


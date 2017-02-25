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


class SectionHeader(object):
    """ Header for a section, consisting of two-letter prefix, title and an optional subtitle. """

    def __init__(self, id_prefix, title, subtitle=''):
        self.__id_prefix = id_prefix
        self.__title = title
        self.__subtitle = subtitle

    def title(self):
        """ Return the title of the section. """
        return self.__title

    def subtitle(self):
        """ Return the subtitle of the section. """
        return self.__subtitle

    def id_prefix(self):
        """ Return the id prefix of the section, a two letter string. """
        return self.__id_prefix


# Section implements __getitem__ but not the complete Container protocol

class Section(object):
    """ Section within a report. """

    def __init__(self, header, metrics, product=None):
        self.__header = header
        self.__metrics = metrics
        self.__product = product
        for index, each_metric in enumerate(self.__metrics):
            each_metric.set_id_string('{pref}-{nr}'.format(pref=self.__header.id_prefix(), nr=index + 1))

    def __str__(self):
        return self.title()

    def __getitem__(self, index):
        return self.__metrics[index]

    def title(self):
        """ Return the title of this section. """
        return self.__header.title()

    def subtitle(self):
        """ Return the subtitle of this section. """
        return self.__header.subtitle()

    def id_prefix(self):
        """ Return the id prefix of this section, a two letter string. """
        return self.__header.id_prefix()

    def metrics(self):
        """ Return the metrics in this section. """
        return self.__metrics

    def product(self):
        """ Return the product this section is about. """
        return self.__product

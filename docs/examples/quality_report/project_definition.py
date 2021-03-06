""" Project definition for the Quality Report software itself. """

###
### BEGIN: This block mocks http calls needed to avoid real http calls and to provide example results instead
### Real report should have those lines removed, in order to contact real metric sources
###
import hqlib.metric_source.url_opener
from tests.url_calls_mocker.url_calls_mocker import UrlOpenerMock
hqlib.metric_source.url_opener.UrlOpener = UrlOpenerMock
### END

import pathlib
import datetime

from hqlib import metric_source, metric, requirement
from hqlib.domain import Project, Environment, Application, Team, Document, TechnicalDebtTarget, \
    DynamicTechnicalDebtTarget


PROJECT_DIR = pathlib.Path(__file__).parent.parent.parent.parent

BUILD_SERVER = metric_source.Jenkins('http://jenkins/', username='jenkins_user', password='jenkins_password',
                                     job_re='-metrics')
JENKINS = metric_source.Jenkins(url='http://www.jenkins.proj.org:8080/')
GIT = metric_source.Git(url='https://github.com/ICTU/quality-report.git')
SONAR = metric_source.Sonar('https://my.sonarqube.com/')
JUNIT=metric_source.JunitTestReport()
HISTORY = metric_source.CompactHistory(PROJECT_DIR / 'docs' / 'examples' / 'quality_report' / 'history.json')
JACOCO = metric_source.JaCoCo(BUILD_SERVER.url() +
                              'job/%s/lastSuccessfulBuild/artifact/trunk/coveragereport/index.html')
ZAP_SCAN_REPORT = metric_source.ZAPScanReport()
SECURITY_REPORT_PROXY = metric_source.FileWithDate()

USER_STORIES_IN_PROGRESS_TRACKER = \
    metric_source.JiraFilter('https://jira.myorg.nl/jira', username="jira_user", password="jira_password")

USER_STORIES_DURATION_TRACKER =  \
    metric_source.JiraFilter('https://jira.myorg.nl/jira', username="jira_user", password="jira_password")

DURATION_MANUAL_TEST_CASES =  \
    metric_source.JiraFilter('https://jira.myorg.nl/jira', username="x", password="y", field_name="customfield_11700")

TRELLO_BOARD = metric_source.TrelloBoard(appkey='2d3', token='57b')

# The project
PROJECT = Project('Organization name', name='Quality Report',
                  metric_sources={
                      metric_source.Jenkins: BUILD_SERVER,
                      metric_source.VersionControlSystem: GIT,
                      metric_source.Sonar: SONAR,
                      metric_source.SystemTestReport: JUNIT,
                      metric_source.JaCoCo: JACOCO,
                      metric_source.ZAPScanReport: ZAP_SCAN_REPORT,
                      metric_source.History: HISTORY,
                      metric_source.CIServer: JENKINS,
                      metric_source.ActionLog: TRELLO_BOARD,
                      metric_source.RiskLog: TRELLO_BOARD,
                      metric_source.UserStoriesInProgressTracker: USER_STORIES_IN_PROGRESS_TRACKER,
                      metric_source.UserStoriesDurationTracker: USER_STORIES_DURATION_TRACKER,
                      metric_source.ManualLogicalTestCaseTracker: DURATION_MANUAL_TEST_CASES,
                      metric_source.UserStoryWithoutSecurityRiskAssessmentTracker: USER_STORIES_IN_PROGRESS_TRACKER,
                      metric_source.UserStoryWithoutPerformanceRiskAssessmentTracker: USER_STORIES_IN_PROGRESS_TRACKER,
                      metric_source.FileWithDate: SECURITY_REPORT_PROXY
                  },
                  metric_source_ids={
                      TRELLO_BOARD: '5fe',
                      DURATION_MANUAL_TEST_CASES: '15999',
                      USER_STORIES_IN_PROGRESS_TRACKER: '15208'
                  },
                  # Override the total LOC metric targets:
                  metric_options={
                      metric.TotalLOC: dict(target=1000000, low_target=2000000)},
                  requirements=[requirement.TrustedProductMaintainability,
                                requirement.TrackManualLTCs,
                                requirement.TrackSecurityAndPerformanceRisks, requirement.TrackActions])

# Teams of the project.
QUALITY_TEAM = Team(name='Quality team', short_name='QU',
                  metric_source_ids={
                      USER_STORIES_IN_PROGRESS_TRACKER: '15208',
                      USER_STORIES_DURATION_TRACKER: '15225',
                  },
                  added_requirements=[requirement.TrackUserStoriesInProgress, requirement.TrackDurationOfUserStories])
PROJECT.add_team(QUALITY_TEAM)

# Documents of the project.
QUALITY_PLAN_URL = 'http://svn/commons/docs/quality_plan.doc'
PROJECT.add_document(Document(name='Quality plan', url=QUALITY_PLAN_URL,
                              metric_source_ids={GIT: QUALITY_PLAN_URL}))

# Development environment of the project
ENVIRONMENT = Environment(name='Environment', short_name='EN', added_requirements=Environment.optional_requirements(),
                          metric_source_ids={SONAR: 'dummy', JENKINS: 'dummy'})
PROJECT.add_environment(ENVIRONMENT)

# Products the project develop(s).
QUALITY_REPORT = Application(
    short_name='QR', name='Example product',
    metric_source_ids={
        SONAR: 'nl.comp:my_project',
        JUNIT: "http://www.junit.report.url/junit.xml",
        JACOCO: 'quality-report-coverage-report',
        GIT: '.',
        ZAP_SCAN_REPORT: 'http://jenkins/job/zap_scan/ws/report.html'},
    metric_options={
        metric.UnittestLineCoverage:
            dict(debt_target=TechnicalDebtTarget(0, 'Sonar incorrectly reports 0% unit test coverage')),
        metric.MajorViolations:
            dict(debt_target=DynamicTechnicalDebtTarget(47, datetime.datetime(2014, 2, 12),
                                                        25, datetime.datetime(2014, 6, 1))),
        metric.UnmergedBranches:
            dict(branches_to_ignore=['spike'], comment="Ignore the spike branch (2016-06-15).")})

SECURITY_REPORT = Document(
    name='Security report',
    url='http://url/to/report',
    added_requirements=[requirement.TrackSecurityTestDate],
    metric_source_ids={
        SECURITY_REPORT_PROXY: 'https://last_security_date_url'
    }
)

PROJECT.add_document(SECURITY_REPORT)

PROJECT.add_product(QUALITY_REPORT)

# Dashboard layout

# Columns in the dashboard is specified as a list of tuples. Each tuple
# contains a column header and the column span.
DASHBOARD_COLUMNS = [('Products', 1), ('Environment', 1), ('Teams', 1)]

# Rows in the dashboard is a list of row tuples. Each row tuple consists of
# tuples that describe a cell in the dashboard. Each cell is a tuple containing
# the product or team and the color. Optionally the cell tuple can contain a
# third value which is a tuple containing the column and row span for the cell.
DASHBOARD_ROWS = [((QUALITY_REPORT, 'lightsteelblue'), (ENVIRONMENT, 'lavender'), (QUALITY_TEAM, 'lavender'))]

PROJECT.set_dashboard(DASHBOARD_COLUMNS, DASHBOARD_ROWS)

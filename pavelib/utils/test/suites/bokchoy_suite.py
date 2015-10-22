"""
Class used for defining and running Bok Choy acceptance test suite
"""
from time import sleep

from paver.easy import sh
from pavelib.utils.test.suites.suite import TestSuite
from pavelib.utils.envs import Env
from pavelib.utils.test import bokchoy_utils
from pavelib.utils.test import utils as test_utils

try:
    from pygments.console import colorize
except ImportError:
    colorize = lambda color, text: text  # pylint: disable=invalid-name

__test__ = False  # do not collect


class BokChoyTestSuite(TestSuite):
    """
    TestSuite for running Bok Choy tests
    Properties (below is a subset):
      test_dir - parent directory for tests
      log_dir - directory for test output
      report_dir - directory for reports (e.g., coverage) related to test execution
      xunit_report - directory for xunit-style output (xml)
      fasttest - when set, skip various set-up tasks (e.g., collectstatic)
      serversonly - prepare and run the necessary servers, only stopping when interrupted with Ctrl-C
      testsonly - assume servers are running (as per above) and run tests with no setup or cleaning of environment
      test_spec - when set, specifies test files, classes, cases, etc. See platform doc.
      default_store - modulestore to use when running tests (split or draft)
    """
    def __init__(self, *args, **kwargs):
        super(BokChoyTestSuite, self).__init__(*args, **kwargs)
        self.test_dir = Env.BOK_CHOY_DIR / kwargs.get('test_dir', 'tests')
        self.log_dir = Env.BOK_CHOY_LOG_DIR
        self.report_dir = Env.BOK_CHOY_REPORT_DIR
        self.xunit_report = self.report_dir / "xunit.xml"
        self.cache = Env.BOK_CHOY_CACHE
        self.fasttest = kwargs.get('fasttest', False)
        self.serversonly = kwargs.get('serversonly', False)
        self.testsonly = kwargs.get('testsonly', False)
        self.test_spec = kwargs.get('test_spec', None)
        self.default_store = kwargs.get('default_store', None)
        self.verbosity = kwargs.get('verbosity', 2)
        self.extra_args = kwargs.get('extra_args', '')
        self.har_dir = self.log_dir / 'hars'
        self.a11y_file = Env.BOK_CHOY_A11Y_CUSTOM_RULES_FILE
        self.imports_dir = kwargs.get('imports_dir', None)

    def __enter__(self):
        super(BokChoyTestSuite, self).__enter__()

        # Ensure that we have a directory to put logs and reports
        self.log_dir.makedirs_p()
        self.har_dir.makedirs_p()
        self.report_dir.makedirs_p()
        test_utils.clean_reports_dir()

        if not (self.fasttest or self.skip_clean):
            test_utils.clean_test_files()

        msg = colorize('green', "Checking for mongo, memchache, and mysql...")
        print msg
        bokchoy_utils.check_services()

        if not self.testsonly:
            self.prepare_bokchoy_run()

        msg = colorize('green', "Confirming servers have started...")
        print msg
        bokchoy_utils.wait_for_test_servers()
        if self.serversonly:
            self.run_servers_continuously()

    def __exit__(self, exc_type, exc_value, traceback):
        super(BokChoyTestSuite, self).__exit__(exc_type, exc_value, traceback)

        msg = colorize('green', "Cleaning up databases...")
        print msg

        # Clean up data we created in the databases
        sh("./manage.py lms --settings bok_choy flush --traceback --noinput")
        bokchoy_utils.clear_mongo()

    def prepare_bokchoy_run(self):
        """
        Sets up and starts servers for a Bok Choy run. If --fasttest is not
        specified then static assets are collected
        """
        sh("{}/scripts/reset-test-db.sh".format(Env.REPO_ROOT))

        if not self.fasttest:
            self.generate_optimized_static_assets()

        # Clear any test data already in Mongo or MySQLand invalidate
        # the cache
        bokchoy_utils.clear_mongo()
        self.cache.flush_all()

        sh(
            "DEFAULT_STORE={default_store}"
            " ./manage.py lms --settings bok_choy loaddata --traceback"
            " common/test/db_fixtures/*.json".format(
                default_store=self.default_store,
            )
        )

        if self.imports_dir:
            sh(
                "DEFAULT_STORE={default_store}"
                " ./manage.py cms --settings=bok_choy import {import_dir}".format(
                    default_store=self.default_store,
                    import_dir=self.imports_dir
                )
            )

        # Ensure the test servers are available
        msg = colorize('green', "Confirming servers are running...")
        print msg
        bokchoy_utils.start_servers(self.default_store)

    def run_servers_continuously(self):
        """
        Infinite loop. Servers will continue to run in the current session unless interrupted.
        """
        print 'Bok-choy servers running. Press Ctrl-C to exit...\n'
        print 'Note: pressing Ctrl-C multiple times can corrupt noseid files and system state. Just press it once.\n'

        while True:
            try:
                sleep(10000)
            except KeyboardInterrupt:
                print "Stopping bok-choy servers.\n"
                break

    @property
    def cmd(self):
        """
        This method composes the nosetests command to send to the terminal. If nosetests aren't being run,
         the command returns an empty string.
        """
        # Default to running all tests if no specific test is specified
        if not self.test_spec:
            test_spec = self.test_dir
        else:
            test_spec = self.test_dir / self.test_spec

        # Skip any additional commands (such as nosetests) if running in
        # servers only mode
        if self.serversonly:
            return ""

        # Construct the nosetests command, specifying where to save
        # screenshots and XUnit XML reports
        cmd = [
            "DEFAULT_STORE={}".format(self.default_store),
            "SCREENSHOT_DIR='{}'".format(self.log_dir),
            "BOK_CHOY_HAR_DIR='{}'".format(self.har_dir),
            "BOKCHOY_A11Y_CUSTOM_RULES_FILE='{}'".format(self.a11y_file),
            "SELENIUM_DRIVER_LOG_DIR='{}'".format(self.log_dir),
            "nosetests",
            test_spec,
            "--with-xunit",
            "--xunit-file={}".format(self.xunit_report),
            "--verbosity={}".format(self.verbosity),
        ]
        if self.pdb:
            cmd.append("--pdb")
        cmd.append(self.extra_args)

        cmd = (" ").join(cmd)
        return cmd

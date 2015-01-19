# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Red Hat Inc. 2013-2014
# Author: Ruda Moura <rmoura@redhat.com>

"""
Base Test Runner Plugins.
"""

from avocado.core import exit_codes
from avocado.plugins import plugin
from avocado.core import output
from avocado import job


class TestRunner(plugin.Plugin):

    """
    Implements the avocado 'run' subcommand
    """

    name = 'test_runner'
    enabled = True
    priority = 0

    def configure(self, parser):
        """
        Add the subparser for the run action.

        :param parser: Main test runner parser.
        """
        self.parser = parser.subcommands.add_parser(
            'run',
            help='Run one or more tests (native test, test alias, binary or script)')

        self.parser.add_argument('url', type=str, default=[], nargs='*',
                                 help='List of test IDs (aliases or paths)')

        self.parser.add_argument('-z', '--archive', action='store_true', default=False,
                                 help='Archive (ZIP) files generated by tests')

        self.parser.add_argument('--keep-tmp-files', action='store_true', default=False,
                                 help='Keep temporary files generated by tests')

        self.parser.add_argument('--force-job-id', dest='unique_job_id',
                                 type=str, default=None,
                                 help=('Forces the use of a particular job ID. Used '
                                       'internally when interacting with an avocado '
                                       'server. You should not use this option '
                                       'unless you know exactly what you\'re doing'))

        out = self.parser.add_argument_group('output related arguments')

        out.add_argument('-s', '--silent', action='store_true', default=False,
                         help='Silence stdout')

        out.add_argument('--show-job-log', action='store_true', default=False,
                         help=('Display only the job log on stdout. Useful '
                               'for test debugging purposes. No output will '
                               'be displayed if you also specify --silent'))

        out.add_argument('--job-log-level', action='store',
                         help=("Log level of the job log. Options: "
                               "'debug', 'info', 'warning', 'error', "
                               "'critical'. Current: debug"),
                         default='debug')

        out_check = self.parser.add_argument_group('output check arguments')

        out_check.add_argument('--output-check-record', type=str,
                               default='none',
                               help=('Record output streams of your tests '
                                     'to reference files (valid options: '
                                     'none (do not record output streams), '
                                     'all (record both stdout and stderr), '
                                     'stdout (record only stderr), '
                                     'stderr (record only stderr). '
                                     'Current: none'))

        out_check.add_argument('--disable-output-check', action='store_true',
                               default=False,
                               help=('Disable test output (stdout/stderr) check. '
                                     'If this option is selected, no output will '
                                     'be checked, even if there are reference files '
                                     'present for the test. '
                                     'Current: False (output check enabled)'))

        mux = self.parser.add_argument_group('multiplex arguments')
        mux.add_argument('-m', '--multiplex-files', nargs='*', default=None,
                         help='Path(s) to a avocado multiplex (.yaml) file(s)')
        mux.add_argument('--filter-only', nargs='*', default=[],
                         help='Filter only path(s) from multiplexing')
        mux.add_argument('--filter-out', nargs='*', default=[],
                         help='Filter out path(s) from multiplexing')

        super(TestRunner, self).configure(self.parser)
        # Export the test runner parser back to the main parser
        parser.runner = self.parser

    def run(self, args):
        """
        Run test modules or simple tests.

        :param args: Command line args received from the run subparser.
        """

        view = output.View(app_args=args, use_paginator=True)
        if args.unique_job_id is not None:
            try:
                int(args.unique_job_id, 16)
                if len(args.unique_job_id) != 40:
                    raise ValueError
            except ValueError:
                view.notify(event='error', msg='Unique Job ID needs to be a 40 digit hex number')
                return exit_codes.AVOCADO_CRASH
        if not args.url:
            self.parser.print_help()
            view.notify(event='error', msg='Empty test ID. A test path or alias must be provided')
            return exit_codes.AVOCADO_CRASH

        job_instance = job.Job(args)
        rc = job_instance.run()
        return rc

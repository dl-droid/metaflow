import os
import platform
import sys

from .util import get_username, to_unicode
from . import metaflow_version
from metaflow.exception import MetaflowException

version_cache = None


class InvalidEnvironmentException(MetaflowException):
    headline = 'Incompatible environment'


class MetaflowEnvironment(object):
    TYPE = 'local'

    def __init__(self, flow):
        pass

    def init_environment(self, logger):
        """
        Run before any step decorators are initialized.
        """
        pass

    def validate_environment(self, logger):
        """
        Run before any command to validate that we are operating in
        a desired environment.
        """
        pass

    def decospecs(self):
        """
        Environment may insert decorators, equivalent to setting --with
        options on the command line.
        """
        return ()

    def bootstrap_commands(self, step_name):
        """
        A list of shell commands to bootstrap this environment in a remote runtime.
        """
        return []

    def add_to_package(self):
        """
        A list of tuples (file, arcname) to add to the job package.
        `arcname` is an alterative name for the file in the job package.
        """
        return []

    def pylint_config(self):
        """
        Environment may override pylint config.
        """
        return []

    @classmethod
    def get_client_info(cls, flow_name, metadata):
        """
        Environment may customize the information returned to the client about the environment

        Parameters
        ----------
        flow_name : str
            Name of the flow
        metadata : dict
            Metadata information regarding the task

        Returns
        -------
        str : Information printed and returned to the user
        """
        return "Local environment"

    def get_package_commands(self, code_package_url, datastore):
        cmds = ["set -e",
                "echo \'Setting up task environment.\'",
                "%s -m pip install click requests \
                    --user -qqq" % self._python(),
                "mkdir metaflow",
                "cd metaflow"]
        env = self
        cmds.extend(datastore.package_download_commands(env, code_package_url))
        return cmds

    def get_environment_info(self):
        global version_cache
        if version_cache is None:
            version_cache = metaflow_version.get_version()

        # note that this dict goes into the code package
        # so variables here should be relatively stable (no
        # timestamps) so the hash won't change all the time
        env = {'platform': platform.system(),
               'username': get_username(),
               'production_token': os.environ.get('METAFLOW_PRODUCTION_TOKEN'),
               'runtime': os.environ.get('METAFLOW_RUNTIME_NAME', 'dev'),
               'app': os.environ.get('APP'),
               'environment_type': self.TYPE,
               'python_version': sys.version,
               'python_version_code': '%d.%d.%d' % sys.version_info[:3],
               'metaflow_version': version_cache,
               'script': os.path.basename(os.path.abspath(sys.argv[0]))}
        return env

    def executable(self, step_name):
        return self._python()

    def _python(self):
        return "python"
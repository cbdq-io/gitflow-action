"""A GitHub Action that enforces and assists with GitFlow."""
import logging
import os
import sys
import json

from git import Repo


class PullRequest:
    """
    Get details of a pull request.

    Attributes
    ----------
    base_branch : str
        The base branch that is being merged into.

    head_branch : str
        The branch being merged from in the pull request.
    """

    def __init__(self) -> None:
        event_path = os.getenv('GITHUB_EVENT_PATH')

        with open(event_path, 'r') as stream:
            event_data = json.load(stream)

        self.base_branch = event_data['pull_request']['base']['ref']
        self.head_branch = event_data['pull_request']['head']['ref']


class GitFlow:
    """
    A class for Git Flow.

    Parameters
    ----------
    main_branch : str
        The name of the main branch (e.g. "main" or "master").
    develop_branch : str
        The name of the develop branch (e.g. "develop").
    version_tag_prefix : str
        The prefix to be applied to version tags.
    release_candidate : str
        The name of the next release.
    prefixes : tuple
        The prefixes for the feature, bugfix, release, hotfix and support
        branches respectively.
    """

    def __init__(self, main_branch: str, develop_branch: str, version_tag_prefix: str, release_candidate: str,
                 *prefixes: tuple) -> None:
        """Create a GitFlow object."""
        self._branch = {
            'main': None,
            'develop': None
        }

        self._prefix = {
            'feature': None,
            'bugfix': None,
            'release': None,
            'hotfix': None,
            'support': None
        }

        self._status = None

        self._logger = None
        logging.basicConfig()
        logger = logging.getLogger('Git Flow')
        logger.setLevel(self.get_log_level())
        self.logger(logger)
        self.status(True)

        event_name = os.getenv('GITHUB_EVENT_NAME', 'push')
        self.event_name(event_name)

        repo = Repo('.')

        if event_name == 'pull_request':
            pr = PullRequest()
            active_branch_name = pr.head_branch
        else:
            active_branch_name = repo.active_branch.name

        self.active_branch(active_branch_name)

        self.main_branch_name(main_branch)
        self.develop_branch_name(develop_branch)
        (
            feature_prefix,
            bugfix_prefix,
            release_prefix,
            hotfix_prefix,
            support_prefix
        ) = prefixes
        self.feature_branch_prefix(feature_prefix)
        self.bugfix_branch_prefix(bugfix_prefix)
        self.release_branch_prefix(release_prefix)
        self.hotfix_branch_prefix(hotfix_prefix)
        self.support_branch_prefix(support_prefix)
        self.version_tag_prefix(version_tag_prefix)
        self.release_candidate(release_candidate)

    def active_branch(self, active_branch: str = None) -> str:
        """
        Get or set the active branch name.

        Parameters
        ----------
        active_branch : str, optional
            The name of the active branch, by default None

        Returns
        -------
        str
            The name of the active branch.
        """
        logger = self.logger()

        if active_branch is not None:
            logger.debug(f'The active branch is "{active_branch}".')
            self._active_branch = active_branch

        return self._active_branch

    def branch_prefix(self, branch_type: str, prefix: str = None) -> str:
        """
        Get or set the prefix for the specified branch type.

        Parameters
        ----------
        branch_type : str
            The branch type (e.g. feature, bugfix, release etc).
        prefix : str, optional
            The prefix for the branch type, by default None

        Returns
        -------
        str
            The prefix for the branch type.
        """
        logger = self.logger()

        if branch_type not in self._prefix.keys():
            logger.error(f'Unknown branch type "{branch_type}".')
            sys.exit(1)

        if prefix is not None:
            logger.debug(f'Prefix for {branch_type} branches is "{prefix}".')
            self._prefix[branch_type] = prefix

        return self._prefix[branch_type]

    def bugfix_branch_prefix(self, bugfix_branch_prefix: str = None) -> str:
        """
        Get or set the bugfix branch prefix.

        Parameters
        ----------
        bugfix_branch_prefix : str, optional
            The bugfix branch prefix, by default None

        Returns
        -------
        str
            The bugfix branch prefix.
        """
        return self.branch_prefix('bugfix', bugfix_branch_prefix)

    def check_base_branch(self, pull_request: PullRequest) -> bool:
        """
        Check that the base branch for a pull request is correct.

        Parameters
        ----------
        pull_request : PullRequest
            A pull request object.

        Returns
        -------
        bool
            True if all is OK, false otherwise.
        """
        logger = self.logger()
        valid_base_branches = [self.develop_branch_name()]

        if self.active_branch().startswith(self.hotfix_branch_prefix()):
            valid_base_branches = [self.main_branch_name()]

            if pull_request.base_branch.startswith(self.support_branch_prefix()):
                valid_base_branches.append(pull_request.base_branch)
        elif self.active_branch().startswith(self.release_branch_prefix()):
            valid_base_branches = [self.main_branch_name()]

        logger.debug(f'Valid base branches are "{", ".join(valid_base_branches)}".')

        if pull_request.base_branch not in valid_base_branches:
            logger.error(f'Base branch "{pull_request.base_branch}" is not suitable for "{pull_request.head_branch}".')
            self.status(False)

        self.check_release_names()

    def check_branch_name(self) -> bool:
        """
        Check the branch name against a list of allowed prefixes.

        Returns
        -------
        bool
            True if the branch name is valid, False otherwise.
        """
        branch_name = self.active_branch()

        if branch_name in [self.main_branch_name(), self.develop_branch_name()]:
            return True

        prefixes = [
            self._prefix['feature'],
            self._prefix['bugfix'],
            self._prefix['release'],
            self._prefix['hotfix'],
            self._prefix['support']
        ]
        return any(branch_name.startswith(prefix) for prefix in prefixes if prefix)

    def check_release_names(self) -> None:
        """
        Check release candidate matches branch name.

        Only relevant if release_candidate is set and active branch is a
        release or hotfix branch.
        """
        release_candidate = self.release_candidate()
        active_branch = self.active_branch()
        hotfix_prefix = self.hotfix_branch_prefix()
        release_prefix = self.release_branch_prefix()
        logger = self.logger()

        if release_candidate == '':
            logger.debug('No release candidate provided.')
            return
        elif not active_branch.startswith(hotfix_prefix) and not active_branch.startswith(release_prefix):
            logger.debug('Not a PR for a hotfix or release branch.')
            return

        branch_tag_name = active_branch.split('/')[-1]
        logger.debug(f'Tag according to branch name is "{branch_tag_name}".')

        if branch_tag_name != release_candidate:
            message = f'Hotfix/release branch is called "{active_branch}" '
            message += 'but release candidate is "{release_candidate}".'
            logger.error(message)
            self.status(False)

    def develop_branch_name(self, develop_branch_name: str = None) -> str:
        """
        Get or set the develop branch name.

        Parameters
        ----------
        develop_branch_name : str, optional
            The develop branch name, by default None

        Returns
        -------
        str
            The develop branch name.
        """
        logger = self.logger()

        if develop_branch_name is not None:
            logger.debug(f'Develop branch name is "{develop_branch_name}".')
            self._branch['develop'] = develop_branch_name

        return self._branch['develop']

    def event_name(self, event_name: str = None) -> str:
        """
        Get or set the event name.

        The event name will either be push, tag or pull_request.

        Parameters
        ----------
        event_name : str
            The event name, by default None

        Returns
        -------
        str
            The event name.
        """
        logger = self.logger()

        if event_name is not None:
            logger.debug(f'Event name is "{event_name}".')
            self._event_name = event_name

        return self._event_name

    def feature_branch_prefix(self, feature_branch_prefix: str = None) -> str:
        """
        Get or set the feature branch prefix.

        Parameters
        ----------
        feature_branch_prefix : str, optional
            The prefix for the feature branches, by default None

        Returns
        -------
        str
            The prefix for the feature branches.
        """
        return self.branch_prefix('feature', feature_branch_prefix)

    def get_log_level(self) -> int:
        """
        Get the log level.

        Returns
        -------
        int
            logging.INFO unless the environment variable ACTIONS_RUNNER_DEBUG
            is set to "true", in which case return logging.DEBUG.
        """
        affirmative_values = ['1', 'true', 'yes']
        actions_runner_debug = os.getenv('ACTIONS_RUNNER_DEBUG', 'false').lower()

        if actions_runner_debug in affirmative_values:
            return logging.DEBUG

        return logging.INFO

    def hotfix_branch_prefix(self, hotfix_branch_prefix: str = None) -> str:
        """
        Get or set the hotfix branch prefix.

        Parameters
        ----------
        hotfix_branch_prefix : str, optional
            The prefix for hotfix branches, by default None

        Returns
        -------
        str
            The prefix for hotfix branches.
        """
        return self.branch_prefix('hotfix', hotfix_branch_prefix)

    def is_ok(self) -> bool:
        """
        Check if validation checks are OK.

        Returns
        -------
        bool
            True if all is OK, false otherwise.
        """
        logger = self.logger()

        if not self.check_branch_name():
            logger.error(f'Branch "{self.active_branch()}" does not follow naming conventions.')
            self.status(False)

        if self.event_name() == 'pull_request':
            pull_request = PullRequest()
            logger.debug(f'Pull request base branch is "{pull_request.base_branch}".')
            logger.debug(f'Pull request head branch is "{pull_request.head_branch}".')
            self.check_base_branch(pull_request)

        return self.status()

    def logger(self, logger: logging.Logger = None) -> logging.Logger:
        """
        Get or set the logger for the Git Flow class.

        Parameters
        ----------
        logger : logging.Logger, optional
            _description_, by default None

        Returns
        -------
        logging.Logger
            _description_
        """
        if logger is not None:
            self._logger = logger

        return self._logger

    def main_branch_name(self, main_branch_name: str = None) -> str:
        """
        Get or set the main branch name.

        Parameters
        ----------
        main_branch_name : str, optional
            The main branch name, by default None

        Returns
        -------
        str
            The main branch name.
        """
        logger = self.logger()

        if main_branch_name is not None:
            logger.debug(f'Main branch name is "{main_branch_name}".')
            self._branch['main'] = main_branch_name

        return self._branch['main']

    def release_branch_prefix(self, release_branch_prefix: str = None) -> str:
        """
        Get or set the release branch prefix.

        Parameters
        ----------
        release_branch_prefix : str, optional
            The release branch prefix, by default None

        Returns
        -------
        str
            The release branch prefix.
        """
        return self.branch_prefix('release', release_branch_prefix)

    def release_candidate(self, release_candidate: str = None) -> str:
        """
        Get or set the release candidate.

        Parameters
        ----------
        release_candidate : str, optional
            The release candidate to be set, by default None

        Returns
        -------
        str
            The release candidate that is set.
        """
        logger = self.logger()

        if release_candidate is not None:
            logger.debug(f'Release candidate is "{release_candidate}".')
            self._release_candidate = release_candidate

        return self._release_candidate

    def status(self, status: bool = None) -> bool:
        """
        Get or set the status.

        True indicates all is OK, false indicates a problem.

        Parameters
        ----------
        status : bool, optional
            The status, by default None

        Returns
        -------
        bool
            The status.
        """
        logger = self.logger()

        if status is not None:
            logger.debug(f'Status is {status}.')
            self._status = status

        return self._status

    def support_branch_prefix(self, support_branch_prefix: str = None) -> str:
        """
        Get or set the support branch prefix.

        Parameters
        ----------
        support_branch_prefix : str, optional
            The prefix for support branches, by default None

        Returns
        -------
        str
            The prefix for support branches.
        """
        return self.branch_prefix('support', support_branch_prefix)

    def version_tag_prefix(self, version_tag_prefix: str = None) -> str:
        """
        Get or set the version tag prefix.

        Parameters
        ----------
        version_tag_prefix : str, optional
            The version tag prefix to be set, by default None

        Returns
        -------
        str
            The set version tag prefix.
        """
        logger = self.logger()

        if version_tag_prefix is not None:
            logger.debug(f'Version tag prefix is "{version_tag_prefix}".')
            self._version_tag_prefix = version_tag_prefix

        return self._version_tag_prefix


if __name__ == '__main__':
    main_branch = sys.argv[1]
    develop_branch = sys.argv[2]
    prefixes = sys.argv[3:8]
    version_tag_prefix = sys.argv[8]
    release_candidate = sys.argv[9]
    gitflow = GitFlow(main_branch, develop_branch, version_tag_prefix, release_candidate, *prefixes)

    if gitflow.is_ok():
        gitflow.logger().debug(f'Command line args were "{sys.argv}".')
        gitflow.logger().info('All is OK.')
        sys.exit(0)

    sys.exit(1)

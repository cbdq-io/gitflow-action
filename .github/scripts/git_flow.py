"""A GitHub Action that enforces and assists with GitFlow."""
import json
import logging
import os
import sys

from fastcore.net import HTTP401UnauthorizedError, HTTP403ForbiddenError
from ghapi.all import GhApi
import nltk

__version__ = '1.0.2'
api = GhApi()


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

        event_name = os.getenv('GITHUB_EVENT_NAME', 'push')
        self.event_name(event_name)

        self.github_repo(os.getenv('GITHUB_REPOSITORY', 'cbdq-io/gitflow-action'))
        self.owner = self.github_repo().split('/')[0]
        self.repo = self.github_repo().split('/')[1]

        if event_name == 'pull_request':
            pr = PullRequest()
            active_branch_name = pr.head_branch
        elif event_name == 'push':
            active_branch_name = os.getenv('GITHUB_REF', develop_branch)

            if active_branch_name.startswith('refs/tags'):
                logger.info('Nothing implemented for pushing tags.')
                self.active_branch(develop_branch)
                return
        else:
            logger.info(f'Nothing implemented for "{event_name}" events.')
            self.active_branch(develop_branch)
            return

        if active_branch_name.startswith('refs/'):
            active_branch_name = '/'.join(active_branch_name.split('/')[2:])

        self.active_branch(active_branch_name)

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
            message += f'but release candidate is "{release_candidate}".'
            logger.error(message)
            self.status(False)

    def create_branch(self, branch_name: str) -> None:
        """
        Create a branch from main to be merged to develop.

        Parameters
        ----------
        branch_name : str
            The name of the branch to be created.
        """
        logger = self.logger()
        existing_branches = api.repos.list_branches(self.owner, self.repo)
        source_sha = None

        for branch in existing_branches:
            if branch.name == branch_name:
                logger.info(f'A branch called "{branch_name}" already exists.')
                return

            if branch.name == self.main_branch_name():
                source_sha = branch.commit.sha

        if not source_sha:
            logger.error(f'Unable to find branch "{self.main_branch_name()}".')
            sys.exit(1)

        logger.debug(f'Creating a branch from {self.main_branch_name()} ({source_sha}).')
        api.git.create_ref(
            self.owner,
            self.repo,
            ref=f'refs/heads/{branch_name}',
            sha=source_sha
        )
        logger.info(f'Successfully created branch "{branch_name}".')

    def create_pull_request(self, base_branch: str, head_branch: str) -> None:
        """
        Create a pull request to develop after a push to main.

        Parameters
        ----------
        base_branch : str
            The name of the base branch (e.g. develop).
        head_branch : str
            The name of the head branch (e.g. bugfix/post-v0.1.0).
        """
        logger = self.logger()
        existing_prs = api.pulls.list(
            self.owner,
            self.repo,
            state='open',
            base=base_branch,
            head=head_branch
        )

        if len(existing_prs) >= 1:
            logger.info(f'A pull request already exists to merge {head_branch} into {base_branch}.')
            return

        logger.info(f'Creating a PR to merge {head_branch} in {base_branch}.')
        body = f"""
        Changes made during release {self.release_candidate()} that are to
        be merged back to {self.develop_branch_name()}.
        """
        nltk.download('punkt_tab')
        body = nltk.word_tokenize(body)
        body = ' '.join(body)
        api.pulls.create(
            self.owner,
            self.repo,
            title=f'Post Release {self.release_candidate()}',
            head=head_branch,
            base=base_branch,
            body=body
        )

    def create_tag(self, tag_name: str) -> None:
        """
        Create a tag in the rep.

        Parameters
        ----------
        tag_name : str
            The name of the tag to be created.
        """
        logger = self.logger()

        if self.is_tag_present(tag_name):
            logger.info(f'A tag called "{tag_name}" already exists.')
        else:
            logger.info(f'Creating a tag "{tag_name}".')
            tag_response = api.git.create_tag(
                self.owner,
                self.repo,
                tag=tag_name,
                object=os.getenv('GITHUB_SHA'),
                type='commit',
                message=tag_name
            )
            api.git.create_ref(
                self.owner,
                self.repo,
                ref=f'refs/tags/{tag_name}',
                sha=tag_response.sha
            )

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

    def github_repo(self, github_repo: str = None) -> str:
        """
        Get or set the GitHub repo name.

        Parameters
        ----------
        github_repo : str, optional
            The GitHub repo to be set, by default None

        Returns
        -------
        str
            The GitHub repo that is set.
        """
        logger = self.logger()

        if github_repo is not None:
            logger.debug(f'GitHub repo is "{github_repo}".')
            self._github_repo = github_repo

        return self._github_repo

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
        elif self.status() and self.is_push_to_main():
            self.push_to_main()

        return self.status()

    def is_push_to_main(self) -> bool:
        """Return True if the GitHub action is due to a push to the main branch."""
        if self.event_name() == 'push' and self.active_branch() == self.main_branch_name():
            return True

        return False

    def is_tag_present(self, tag_name: str) -> bool:
        """
        Check if tag exists in a repo.

        Parameters
        ----------
        tag_name : str
            The name of the tag to check for.

        Returns
        -------
        bool
            Return true if tag exists.
        """
        existing_tags = api.repos.list_tags(self.owner, self.repo)

        for tag in existing_tags:
            if tag_name == tag.name:
                return True

        return False

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

    def push_to_main(self) -> bool:
        """Run processes after pushing to main."""
        logger = self.logger()

        if not self.release_candidate():
            logger.debug(f'No release candidate so nothing to be done after push to {self.main_branch_name()}.')
            return

        display_tag = self.version_tag_prefix() + self.release_candidate()
        self.create_tag(display_tag)
        branch_name = f'{self.bugfix_branch_prefix()}post-{display_tag}'
        self.create_branch(branch_name)
        self.create_pull_request(self.develop_branch_name(), branch_name)

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

    try:
        if gitflow.is_ok():
            gitflow.logger().debug(f'Command line args were "{sys.argv}".')
            gitflow.logger().info('All is OK.')
            sys.exit(0)
    except HTTP403ForbiddenError as ex:
        gitflow.logger().error(ex)
    except HTTP401UnauthorizedError as ex:
        gitflow.logger().error(ex)

    sys.exit(1)

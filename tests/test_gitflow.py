"""GitFlow Class feature tests."""

import json
import os
import sys

from pytest_bdd import given, parsers, scenario, then, when

sys.path.append('.github/scripts')


@scenario('features/gitflow.feature', 'Invalid Pull Requests')
def test_invalid_pull_requests():
    """Invalid Pull Requests."""


@scenario('features/gitflow.feature', 'Invalid Pushes')
def test_invalid_pushes():
    """Invalid Pushes."""


@scenario('features/gitflow.feature', 'Post Release Assignee Handling')
def test_post_release_assignee_handling():
    """Post Release Assignee Handling."""


@scenario('features/gitflow.feature', 'Valid Pull Requests')
def test_valid_pull_requests():
    """Valid Pull Requests."""


@scenario('features/gitflow.feature', 'Valid Pushes')
def test_valid_pushes():
    """Valid Pushes."""


@given('the GitFlow develop branch is "develop"', target_fixture='gitflow_develop_branch')
def _():
    """the GitFlow develop branch is "develop"."""
    return 'develop'


@given('the GitFlow main branch is "main"', target_fixture='gitflow_main_branch')
def _():
    """the GitFlow main branch is "main"."""
    return 'main'


@given('the GitFlow prefixes are the standard prefixes', target_fixture='gitflow_prefixes')
def _():
    """the GitFlow prefixes are the standard prefixes."""
    return ('feature/', 'bugfix/', 'release/', 'hotfix/', 'support/')


@given(
    parsers.parse('the GitFlow release candidate is {release_candidate}'), target_fixture='gitflow_release_candidate'
)
def _(release_candidate: str):
    """the GitFlow release candidate is <release_candidate>."""
    return release_candidate


@given(
    parsers.parse('the GitFlow version tag prefix is {version_tag_prefix}'), target_fixture='gitflow_version_tag_prefix'
)
def _(version_tag_prefix: str):
    """the GitFlow version tag prefix is <version_tag_prefix>."""
    return version_tag_prefix


@when(
    parsers.parse('the GitFlow post-release assignee string is {post_release_pr_assignees}'),
    target_fixture='post_release_pr_assignees',
)
def _(post_release_pr_assignees: str):
    """the GitFlow post-release assignee string is <post_release_pr_assignees>."""
    if post_release_pr_assignees == 'N/A':
        post_release_pr_assignees = ''

    return post_release_pr_assignees


@when(parsers.parse('the GitHub event name is {github_event_name}'), target_fixture='github_event_name')
def _(github_event_name: str):
    """the GitHub event name is <github_event_name>."""
    return github_event_name


@when(parsers.parse('the GitHub head branch is {github_head_branch}'), target_fixture='github_head_branch')
def _(github_head_branch: str):
    """the GitHub head branch is <github_head_branch>."""
    return github_head_branch


@when(parsers.parse('the GitHub ref is {github_ref}'), target_fixture='github_ref')
def _(github_ref: str):
    """the GitHub ref is <github_ref>."""
    return github_ref


@when('the GitHub repository is "cbdq-io/gitflow-action"', target_fixture='github_repository')
def _():
    """the GitHub repository is "cbdq-io/gitflow-action"."""
    return 'cbdq-io/gitflow-action'


@then(parsers.parse('the assignee count is {expected_assignee_count:d}'))
def _(
    expected_assignee_count: int,
    gitflow_main_branch: str,
    gitflow_develop_branch: str,
    gitflow_version_tag_prefix: str,
    gitflow_release_candidate: str,
    gitflow_prefixes: tuple[str],
    github_ref: str,
    github_event_name: str,
    github_head_branch: str,
    post_release_pr_assignees: str,
):
    """the GitFlow post-release assignee string is <post_release_pr_assignees>."""
    from git_flow import GitFlow

    mock_github_payload_event = '/tmp/mock_github_payload_event.json'  # noqa

    os.environ['GITHUB_EVENT_NAME'] = github_event_name
    os.environ['GITHUB_EVENT_PATH'] = mock_github_payload_event
    os.environ['GITHUB_REF'] = github_ref
    os.environ['ACTIONS_RUNNER_DEBUG'] = '1'

    if github_event_name == 'pull_request':
        payload = {'pull_request': {'base': {'ref': github_ref}, 'head': {'ref': github_head_branch}}}

        with open(mock_github_payload_event, 'wt') as stream:
            json.dump(payload, stream)

    if gitflow_release_candidate == 'N/A':
        gitflow_release_candidate = ''

    gitflow = GitFlow(
        gitflow_main_branch,
        gitflow_develop_branch,
        gitflow_version_tag_prefix,
        gitflow_release_candidate,
        post_release_pr_assignees,
        *gitflow_prefixes,
    )
    assert gitflow.is_ok()
    actual_assignee_count = len(gitflow.post_release_pr_assignees())
    message = f'Expected {expected_assignee_count} assignees, but it is {actual_assignee_count}.'
    assert actual_assignee_count == expected_assignee_count, message


@then(parsers.parse('the expected outcome is {expected_outcome}'))
def _(
    expected_outcome: str,
    gitflow_main_branch: str,
    gitflow_develop_branch: str,
    gitflow_version_tag_prefix: str,
    gitflow_release_candidate: str,
    gitflow_prefixes: tuple[str],
    github_ref: str,
    github_event_name: str,
    github_head_branch: str,
):
    """the expected outcome is <expected_outcome>."""
    from git_flow import GitFlow

    mock_github_payload_event = '/tmp/mock_github_payload_event.json'  # noqa

    os.environ['GITHUB_EVENT_NAME'] = github_event_name
    os.environ['GITHUB_EVENT_PATH'] = mock_github_payload_event
    os.environ['GITHUB_REF'] = github_ref
    os.environ['ACTIONS_RUNNER_DEBUG'] = '1'

    if github_event_name == 'pull_request':
        payload = {'pull_request': {'base': {'ref': github_ref}, 'head': {'ref': github_head_branch}}}

        with open(mock_github_payload_event, 'wt') as stream:
            json.dump(payload, stream)

    if gitflow_release_candidate == 'N/A':
        gitflow_release_candidate = ''

    gitflow = GitFlow(
        gitflow_main_branch,
        gitflow_develop_branch,
        gitflow_version_tag_prefix,
        gitflow_release_candidate,
        '',
        *gitflow_prefixes,
    )
    expected_outcome = expected_outcome == 'True'
    actual_outcome = gitflow.is_ok()
    assert actual_outcome == expected_outcome

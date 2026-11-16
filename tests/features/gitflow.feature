Feature: GitFlow Class

  Scenario Outline: Valid Pushes
    Given the GitFlow main branch is "main"
    And the GitFlow develop branch is "develop"
    And the GitFlow version tag prefix is <version_tag_prefix>
    And the GitFlow release candidate is <release_candidate>
    And the GitFlow prefixes are the standard prefixes
    When the GitHub event name is <github_event_name>
    And the GitHub head branch is <github_head_branch>
    And the GitHub repository is "cbdq-io/gitflow-action"
    And the GitHub ref is <github_ref>
    Then the expected outcome is <expected_outcome>

    Examples:
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch | github_ref                | expected_outcome |
        | v                  | 0.1.0             | push              | main               | refs/tags/0.1.0           | True             |
        | v                  | 0.1.0             | push              | N/A                | develop                   | True             |
        | v                  | 0.1.0             | tag               | main               | refs/tags/0.1.0           | True             |
        | v                  | N/A               | push              | N/A                | support/v1                | True             |
        | v                  | N/A               | push              | N/A                | support/v1/hotfix/1.42.42 | True             |

  Scenario Outline: Invalid Pushes
    Given the GitFlow main branch is "main"
    And the GitFlow develop branch is "develop"
    And the GitFlow version tag prefix is <version_tag_prefix>
    And the GitFlow release candidate is <release_candidate>
    And the GitFlow prefixes are the standard prefixes
    When the GitHub event name is <github_event_name>
    And the GitHub head branch is <github_head_branch>
    And the GitHub repository is "cbdq-io/gitflow-action"
    And the GitHub ref is <github_ref>
    Then the expected outcome is <expected_outcome>

    Examples:
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch | github_ref                 | expected_outcome |
        | v                  | 0.1.0             | push              | N/A                | foo                        | False            |
        | v                  | 0.1.0             | push              | N/A                | support/v1/1.42.42         | False            |
        | v                  | 0.1.0             | push              | N/A                | support/v1/feature/1.42.42 | False            |

  Scenario Outline: Valid Pull Requests
    Given the GitFlow main branch is "main"
    And the GitFlow develop branch is "develop"
    And the GitFlow version tag prefix is <version_tag_prefix>
    And the GitFlow release candidate is <release_candidate>
    And the GitFlow prefixes are the standard prefixes
    When the GitHub event name is <github_event_name>
    And the GitHub head branch is <github_head_branch>
    And the GitHub repository is "cbdq-io/gitflow-action"
    And the GitHub ref is <github_ref>
    Then the expected outcome is <expected_outcome>

    Examples:
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch        | github_ref      | expected_outcome |
        | v                  | 0.1.0             | pull_request      | bugfix/foo                | develop         | True             |
        | v                  | 0.1.0             | pull_request      | hotfix/0.1.0              | main            | True             |
        | v                  | N/A               | pull_request      | release/0.1.1             | main            | True             |
        | v                  | 1.42.42           | pull_request      | support/v1/hotfix/1.42.42 | support/v1      | True             |

  Scenario Outline: Invalid Pull Requests
    Given the GitFlow main branch is "main"
    And the GitFlow develop branch is "develop"
    And the GitFlow version tag prefix is <version_tag_prefix>
    And the GitFlow release candidate is <release_candidate>
    And the GitFlow prefixes are the standard prefixes
    When the GitHub event name is <github_event_name>
    And the GitHub head branch is <github_head_branch>
    And the GitHub repository is "cbdq-io/gitflow-action"
    And the GitHub ref is <github_ref>
    Then the expected outcome is <expected_outcome>

    Examples:
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch        | github_ref      | expected_outcome |
        | v                  | 0.1.0             | pull_request      | fix/foo                   | develop         | False            |
        | v                  | 0.1.0             | pull_request      | release/0.1.0             | develop         | False            |
        | v                  | 0.1.0             | pull_request      | release/0.1.1             | main            | False            |
        | v                  | 0.1.0             | pull_request      | hotfix/0.1.1              | develop         | False            |
        | v                  | N/A               | pull_request      | support/v1/hotfix/1.42.42 | main            | False            |
        | v                  | 0.1.0             | pull_request      | support/v1/hotfix/1.42.42 | support/v1      | False            |
        | v                  | 1.42.42           | pull_request      | support/v2/hotfix/1.42.42 | support/v1      | False            |

  Scenario Outline: Post Release Assignee Handling
    Given the GitFlow main branch is "main"
    And the GitFlow develop branch is "develop"
    And the GitFlow version tag prefix is <version_tag_prefix>
    And the GitFlow release candidate is <release_candidate>
    And the GitFlow prefixes are the standard prefixes
    When the GitHub event name is <github_event_name>
    And the GitHub head branch is <github_head_branch>
    And the GitHub repository is "cbdq-io/gitflow-action"
    And the GitHub ref is <github_ref>
    And the GitFlow post-release assignee string is <post_release_pr_assignees>
    Then the assignee count is <assignee_count>

    Examples:
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch | github_ref      | post_release_pr_assignees | assignee_count |
        | v                  | 0.1.0             | pull_request      | bugfix/foo         | develop         | N/A                       | 0              |
        | v                  | 0.1.0             | pull_request      | bugfix/foo         | develop         | cbdqbot                   | 1              |
        | v                  | 0.1.0             | pull_request      | bugfix/foo         | develop         | cbdqbot,dallinb           | 2              |
        | v                  | 0.1.0             | pull_request      | bugfix/foo         | develop         | cbdqbot,dallinb,          | 2              |
        | v                  | 0.1.0             | pull_request      | bugfix/foo         | develop         | cbdqbot,,dallinb          | 2              |

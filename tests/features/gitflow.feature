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
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch | github_ref      | expected_outcome |
        | v                  | 0.1.0             | push              | main               | refs/tags/0.1.0 | True             |
        | v                  | 0.1.0             | push              | N/A                | develop         | True             |
        | v                  | 0.1.0             | tag               | main               | refs/tags/0.1.0 | True             |

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
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch | github_ref      | expected_outcome |
        | v                  | 0.1.0             | push              | N/A                | foo             | False            |

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
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch | github_ref      | expected_outcome |
        | v                  | 0.1.0             | pull_request      | bugfix/foo         | develop         | True             |
        | v                  | 0.1.0             | pull_request      | hotfix/0.1.0       | main            | True             |
        | v                  | N/A               | pull_request      | release/0.1.1      | main            | True             |

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
        | version_tag_prefix | release_candidate | github_event_name | github_head_branch | github_ref      | expected_outcome |
        | v                  | 0.1.0             | pull_request      | fix/foo            | develop         | False            |
        | v                  | 0.1.0             | pull_request      | release/0.1.0      | develop         | False            |
        | v                  | 0.1.0             | pull_request      | release/0.1.1      | main            | False            |
        | v                  | 0.1.0             | pull_request      | hotfix/0.1.1       | develop         | False            |

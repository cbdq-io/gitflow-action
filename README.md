# Git Flow Action

A GitHub Action that enforces and assists with GitFlow.

## Parameters

| Parameter | Description | Default |
| --------- | ----------- | ------- |
| bugfix-prefix | The prefix of bugfix branches | bugfix/ |
| develop-branch-name | The name of the develop branch. | develop |
| feature-prefix | Prefix for feature branches | feature/ |
| hotfix-prefix | Prefix for bugfix branches | hotfix/ |
| main-branch-name | The name of the main branch | main |
| release-candidate | If set (non-blank), will complete releases on pushes to the main branch. | "" |
| release-prefix | Prefix for release branches | release/ |
| support-prefix | Prefix for support branches | support/ |
| version-tag-prefix | A prefix (e.g. "v") to be applied to any tag. | "" |

## Examples

In this example, the release-candidate is being set to the contents of a
file called `VERSION`.

```yaml
---
name: Git Flow

on:
  # Run on any pull request, or any push of a branch (avoiding pushing of
  # tags).
  pull_request:
    branches:
      - '*'
      - '**'
  push:
    branches:
      - '*'
      - '**'
    tags:
      - '!*'  # This excludes all tags

jobs:
  GitFlow:

    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Retrieve Release Candidate Name
        id: version
        run: echo "RELEASE_CANDIDATE_TAG=$( cat VERSION )" >> $GITHUB_OUTPUT

      - name: Git Flow Action
        uses: cbdq-io/gitflow-action@feature/mvp
        env:
          # Setting this environment variable means we can debug by re-running
          # workflows and ticking "Enable debug logging".
          ACTIONS_RUNNER_DEBUG: ${{ runner.debug }}

          GITHUB_TOKEN: ${{ secrets.BOT_TOKEN }}
        with:
          # Set the release candidate to be the output of the previous step.
          release-candidate: ${{ steps.version.outputs.RELEASE_CANDIDATE_TAG }}
```

## Token

The token passed to the action must have the following
[repository permissions](https://github.com/settings/personal-access-tokens):

| Permission | Description | Notes |
| ---------- | ----------- | ----- |
| Contents   | Repository contents, commits, branches, downloads, releases, and merges. | Required to check/create branches and tags. |
| Metadata   | Search repositories, list collaborators, and access repository metadata. | Every fine-grained token has this set. |
| Pull requests | Pull requests and related comments, assignees, labels, milestones, and merges. | required to raise the pull request after a release/hotfix. |

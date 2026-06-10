# Changelog


## Unreleased

### Fix

* Remove CVE-2026-42215 vulnerability. [Ben Dalling]

* Remove CVE-2025-14009 vulnerability. [Ben Dalling]

### Build

* Bump actions/setup-python from 5 to 6. [dependabot[bot]]

  Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 6.
  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v5...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/setup-python
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...

* Bump actions/checkout from 4 to 6. [dependabot[bot]]

  Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 6.
  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v4...v6)

  ---
  updated-dependencies:
  - dependency-name: actions/checkout
    dependency-version: '6'
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...

* Bump wheel from 0.43.0 to 0.46.2 in /.github/requirements. [dependabot[bot]]

  Bumps [wheel](https://github.com/pypa/wheel) from 0.43.0 to 0.46.2.
  - [Release notes](https://github.com/pypa/wheel/releases)
  - [Changelog](https://github.com/pypa/wheel/blob/main/docs/news.rst)
  - [Commits](https://github.com/pypa/wheel/compare/0.43.0...0.46.2)

  ---
  updated-dependencies:
  - dependency-name: wheel
    dependency-version: 0.46.2
    dependency-type: direct:production
  ...


## 1.0.3 (2025-07-17)

### Fix

* Refine logic for when post-release PR is skipped. [Ben Dalling]

### Build

* Release/1.0.3. [Ben Dalling]

* Bump setuptools in /.github/requirements. [dependabot[bot]]

  Bumps [setuptools](https://github.com/pypa/setuptools) from 70.0.0 to 78.1.1.
  - [Release notes](https://github.com/pypa/setuptools/releases)
  - [Changelog](https://github.com/pypa/setuptools/blob/main/NEWS.rst)
  - [Commits](https://github.com/pypa/setuptools/compare/v70.0.0...v78.1.1)

  ---
  updated-dependencies:
  - dependency-name: setuptools
    dependency-version: 78.1.1
    dependency-type: direct:production
  ...


## 1.0.2 (2024-08-24)

### Fix

* Catch HTTP401UnauthorizedError exceptions. [Ben Dalling]

* Tidy up the text in the PR body. [Ben Dalling]

### Build

* Bump setuptools in /.github/requirements. [dependabot[bot]]

  Bumps [setuptools](https://github.com/pypa/setuptools) from 69.2.0 to 70.0.0.
  - [Release notes](https://github.com/pypa/setuptools/releases)
  - [Changelog](https://github.com/pypa/setuptools/blob/main/NEWS.rst)
  - [Commits](https://github.com/pypa/setuptools/compare/v69.2.0...v70.0.0)

  ---
  updated-dependencies:
  - dependency-name: setuptools
    dependency-type: direct:production
  ...


## 1.0.1 (2024-05-04)

### Fix

* GitHub workflow refactor. [Ben Dalling]


## 1.0.0 (2024-05-04)

### Fix

* Reduce number of API calls. [Ben Dalling]

* PR issues (II). [Ben Dalling]

* PR issues. [Ben Dalling]

* Correct check_branch_name (II). [Ben Dalling]

* Correct check_branch_name. [Ben Dalling]

### New

* Add details to the README. [Ben Dalling]

* Create branch and pr after push to main. [Ben Dalling]

* Create a tag on push to main. [Ben Dalling]

* Check for the existence of the tag in GitHub. [Ben Dalling]

* Validate hotfix/release branch names against the release candidate tag. [Ben Dalling]

* Add the release candidate option. [Ben Dalling]

* Convert to a Docker action. [Ben Dalling]

* Allow a version tag prefix to be specified. [Ben Dalling]

* Validate push branch names and pull request base branches. [Ben Dalling]



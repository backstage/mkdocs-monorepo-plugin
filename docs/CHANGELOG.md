# Changelog

## 1.0.4

-   Resolve a bug that prevented this plugin from working with mkdocs >= v1.4.0

## 1.0.3

-   Allow no specification for both ´nav´ and ´docs_dir´

## 1.0.2

-   Fixed edit URLs to use realpath of pages

## 1.0.1

-   Fixed edit URLs for included pages

## 1.0.0

-   This package has been promoted to v1.0!

> **Note:** Going forward, this package will follow [semver](https://semver.org/#semantic-versioning-200) conventions.

## 0.5.3

-   Don't run on_serve if on_config was skipped

## 0.5.2

-   Add support for wildcard include statement

## 0.5.1

-   Fix `No module named 'slugify'` error when installing in mkdocs environments.

## 0.5.0

-   Allow `mkdocs.yaml` in addition to `mkdocs.yml`
-   Drops support for Python 3.5 (because the minimum `mkdocs` version which
  supports the above feature no longer supports it).

## 0.4.18

-   Allow inclusion of sub-docs `mkdocs.yml` even if its name isn't URL-friendly.
  Works by slugifying non-URL friendly names. (#58)

## 0.4.17

-   Fixed bug where URLs in an included `mkdocs.yml` were prefixed by the `site_name` and thus did not support absolute URLs.

## 0.4.16

-   Fix `mkdocs serve` incompatibility when running with mkdocs >= 1.2

## 0.4.15

-   Allow automatic `nav` generation if `docs_dir` is specified in the sub-docs `mkdocs.yml` file (#35)

## 0.4.14

-   Now respects the `docs_dir` config in `mkdocs.yml` (#44)

## 0.4.13

-   Allow other plugins to manipulate the source directory (#42)

## 0.4.12

-   Allow any config file name and not just `mkdocs.yml` (#36)

## 0.4.11

-   Moved repository to the Backstage organization

## 0.4.10

-   New fix for previous issue which doesn't break when site_name contains a slash

## 0.4.9

-   Fix issue using plugin on Windows when site_name contains slash

## 0.4.8

-   Dropped support for Python 3.4 in `setup.py`

## 0.4.6

-   Fixes [compatibility issue with `mkdocs-git-revision-date-localized-plugin`](https://github.com/backstage/mkdocs-monorepo-plugin/issues/12)

## 0.4.5

-   Bumped up `mkdocs` to 1.1.1 and added compatibility (gh-16)

## 0.4.4

-   Bumped up `mkdocs` to 1.1 and `mkdocs-material` to 5.1.0

## 0.4.3

-   Fixed bug with trailing slash in Windows ([#9](https://github.com/backstage/mkdocs-monorepo-plugin/pull/9))
-   Fixed bug with README

## 0.4.1

-   Fixed bug with root `docs/` folder not working with livereload
-   Fixed bug with `mkdocs.yml` in subfolders not working with livereload

## 0.4.0

-   Initial release.

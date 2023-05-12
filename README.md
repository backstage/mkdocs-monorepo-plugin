# backstage/mkdocs-monorepo-plugin

[![](https://github.com/backstage/mkdocs-monorepo-plugin/workflows/Build%2C%20Test%20%26%20Deploy/badge.svg)](https://github.com/backstage/mkdocs-monorepo-plugin/actions)
[![PyPI](https://img.shields.io/pypi/v/mkdocs-monorepo-plugin)](https://pypi.org/project/mkdocs-monorepo-plugin/)
![](https://img.shields.io/badge/lifecycle-stable-509bf5.svg)
[![PyPI - License](https://img.shields.io/pypi/l/mkdocs-monorepo-plugin)](LICENSE)

✚ This plugin enables you to build multiple sets of documentation in a single Mkdocs. It is designed to address writing documentation in Spotify's largest and most business-critical codebases (typically monoliths or monorepos).

✏️ [Blog Post](https://labs.spotify.com/2019/10/01/solving-documentation-for-monoliths-and-monorepos/) | 🐍 [Python Package](https://pypi.org/project/mkdocs-monorepo-plugin/) | ✚ [Demo](https://backstage.github.io/mkdocs-monorepo-plugin/monorepo-example/) | 📕 [Docs](https://backstage.github.io/mkdocs-monorepo-plugin/)

## Features

- **Support for multiple `docs/` folders in Mkdocs.** Having a single `docs/` folder in a large codebase is hard to maintain. Who owns which documentation? What code is it associated with? Bringing docs closer to the associated code enables you to update them better, as well as leverage folder-based features such as [GitHub Codeowners].

- **Support for multiple navigations.** In Spotify, large repositories typically are split up by multiple owners. These are split by folders. By introducing multiple `mkdocs.yml` files along with multiple `docs/` folder, each team can take ownership of their own navigation. This plugin then intelligently merges of the documentation together into a single repository.

- **Support across multiple repositories.** Using [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) it is possible to merge documentation across multiple repositories into a single codebase dynamically.

- **The same great Mkdocs developer experience.** It is possible to run `mkdocs serve` in the root to merge all of your documentation together, or in a subfolder to build specific documentation. Autoreload still works as usual. No more using [symlinks](https://devdojo.com/tutorials/what-is-a-symlink)!

## Install

It's easy to get started using [PyPI] and `pip` using Python:

```terminal
$ pip install mkdocs-monorepo-plugin
```

## Usage

Take a look in [our sample project](./sample-docs) for an example implementation, or see [what it looks like after running `mkdocs build`](https://backstage.github.io/mkdocs-monorepo-plugin/monorepo-example/).

In general, this plugin introduces the `!include` syntax in your Mkdocs navigation structure and then merges them together.

```yaml
# /mkdocs.yml
site_name: Cats API

nav:
  - Intro: 'index.md'
  - Authentication: 'authentication.md'
  - API:
    - v1: '!include ./v1/mkdocs.yml'
    - v2: '!include ./v2/mkdocs.yml'

plugins:
  - monorepo

```
```yaml
# /src/v1/mkdocs.yml
site_name: versions/v1

nav:
  - Reference: "reference.md"
  - Changelog: "changelog.md"

```
```yaml
# /src/v2/mkdocs.yml
site_name: versions/v2

nav:
  - Migrating to v2: "migrating.md"
  - Reference: "reference.md"
  - Changelog: "changelog.md"

```

#### Example Source Filetree

```terminal
$ tree .

├── docs
│   ├── authentication.md
│   └── index.md
├── mkdocs.yml
├── v1
│   ├── docs
│   │   ├── changelog.md
│   │   └── reference.md
│   └── mkdocs.yml
└── v2
    ├── docs
    │   ├── changelog.md
    │   ├── migrating.md
    │   └── reference.md
    └── mkdocs.yml

5 directories, 10 files
```

#### Example Rendered Filetree

```
$ mkdocs build
$ tree ./site

├── 404.html
├── authentication
│   └── index.html
├── css
│   ├── base.css
│   ├── bootstrap-custom.min.css
│   └── font-awesome.min.css
├── fonts
│   ├── fontawesome-webfont.eot
│   ├── fontawesome-webfont.svg
│   ├── fontawesome-webfont.ttf
│   ├── fontawesome-webfont.woff
│   ├── fontawesome-webfont.woff2
│   ├── glyphicons-halflings-regular.eot
│   ├── glyphicons-halflings-regular.svg
│   ├── glyphicons-halflings-regular.ttf
│   ├── glyphicons-halflings-regular.woff
│   └── glyphicons-halflings-regular.woff2
├── img
│   ├── favicon.ico
│   └── grid.png
├── index.html
├── js
│   ├── base.js
│   ├── bootstrap-3.0.3.min.js
│   └── jquery-1.10.2.min.js
├── sitemap.xml
├── sitemap.xml.gz
└── versions
    ├── v1
    │   ├── changelog
    │   │   └── index.html
    │   └── reference
    │       └── index.html
    └── v2
        ├── changelog
        │   └── index.html
        ├── migrating
        │   └── index.html
        └── reference
            └── index.html

13 directories, 28 files
```

Note that, as of `v0.5.2`, the `*include` syntax can be used in place of `!include` in order to compile any number of `mkdocs.yml` files that match a glob-like pattern, without having to specify every one individually. For example:


```yaml
# /mkdocs.yml
site_name: Cats System

nav:
  - Intro: 'index.md'
  - Components: '*include ./components/*/mkdocs.yml'
```

#### Example Source Filetree

```terminal
$ tree .

├── components
│   ├── belly-rubs
│   │   ├── docs
│   │   |   └── index.md
│   │   └── mkdocs.yml
|   ├── purring
│   │   ├── docs
│   │   |   └── index.md
│   │   └── mkdocs.yml
|   └── skritches
│   │   ├── docs
│   │   |   └── index.md
│   │   └── mkdocs.yml
├── docs
│   └── index.md
└── mkdocs.yml

8 directories, 8 files
```

### Release

1. Update the [CHANGELOG.md](./docs/CHANGELOG.md).
2. Bump up the version number in `setup.py` which triggers the release workflow on [GitHub Actions](.github/workflows/deploy.yml) to publish a new version in PyPI.

## Supported Versions

- Python 3 &mdash; 3.7, 3.8, 3.9, 3.10, 3.11
- [Mkdocs] 1.0.4 and above.

## Changelog

Check out our [CHANGELOG.md](./docs/CHANGELOG.md) for details.

## License

Copyright 2020-2021 © The Backstage Authors. All rights reserved. The Linux Foundation has registered trademarks and uses trademarks. For a list of trademarks of The Linux Foundation, please see our Trademark Usage page: https://www.linuxfoundation.org/trademark-usage

Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0

## Contributing

Check out our [CONTRIBUTING](./docs/CONTRIBUTING.md) for more details.

[mkdocs/mkdocs]: https://github.com/mkdocs/mkdocs
[mkdocs-plugin-template]: https://github.com/byrnereese/mkdocs-plugin-template
[pypi]: https://pypi.org
[mkdocs]: https://www.mkdocs.org
[github codeowners]: https://help.github.com/en/articles/about-code-owners

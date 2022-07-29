# Copyright 2020 The Backstage Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import copy
import re
from pathlib import Path

from slugify import slugify
from mkdocs.utils import yaml_load, warning_filter, dirname_to_title, get_markdown_title
from urllib.parse import urlsplit
log = logging.getLogger(__name__)
log.addFilter(warning_filter)

INCLUDE_STATEMENT = "!include "
WILDCARD_INCLUDE_STATEMENT = "*include "


class Parser:
    def __init__(self, config):
        self.initialNav = config['nav']
        self.config = config

    def __loadAliasesAndResolvedPaths(self, nav=None):
        if nav is None:
            nav = copy.deepcopy(self.initialNav)

        paths = []

        for index, item in enumerate(nav):
            if type(item) is str:
                value = str
            elif type(item) is dict:
                value = list(item.values())[0]
                if type(value) is str and value.startswith(WILDCARD_INCLUDE_STATEMENT):
                    root_dir = Path(self.config['config_file_path']).parent
                    mkdocs_path = value[len(WILDCARD_INCLUDE_STATEMENT):]
                    dirs = sorted(root_dir.glob(mkdocs_path))
                    if dirs:
                        value = []
                        for mkdocs_config in dirs:
                            site = {}
                            if os.path.exists(mkdocs_config):
                                site[str(mkdocs_config)] = f"{INCLUDE_STATEMENT}{mkdocs_config.resolve()}"
                                value.append(site)
            else:
                value = None

            if type(value) is str and value.startswith(INCLUDE_STATEMENT):
                paths.append(value[len(INCLUDE_STATEMENT):])
            elif type(value) is list:
                paths.extend(self.__loadAliasesAndResolvedPaths(value))

        return paths

    def getResolvedPaths(self):
        """Return list of [alias, docs_dir, mkdocs.yml]."""
        def extractAliasAndPath(absPath):
            loader = IncludeNavLoader(self.config, absPath).read()
            alias = loader.getAlias()
            docsDir = os.path.join(loader.rootDir, os.path.dirname(absPath), loader.getDocsDir())
            return [alias, docsDir, os.path.join(loader.rootDir, absPath)]

        resolvedPaths = list(
            map(extractAliasAndPath, self.__loadAliasesAndResolvedPaths()))

        for alias, docsDir, ymlPath in resolvedPaths:
            if not os.path.exists(docsDir):
                log.critical(
                    "[mkdocs-monorepo] The {} path is not valid. ".format(docsDir) +
                    "Please update your 'nav' with a valid path.")
                raise SystemExit(1)

        return resolvedPaths

    def resolve(self, nav=None):
        if nav is None:
            nav = copy.deepcopy(self.initialNav)

        for index, item in enumerate(nav):
            if type(item) is str:
                key = None
                value = item
            elif type(item) is dict:
                key = list(item.keys())[0]
                value = list(item.values())[0]
                if type(value) is str and value.startswith(WILDCARD_INCLUDE_STATEMENT):
                    root_dir = Path(self.config['config_file_path']).parent
                    mkdocs_path = value[len(WILDCARD_INCLUDE_STATEMENT):]
                    if not mkdocs_path.endswith(tuple([".yml", ".yaml"])):
                        log.critical(
                            "[mkdocs-monorepo] The wildcard include path {} does not end with .yml (or .yaml)".format(
                                mkdocs_path)
                        )
                        raise SystemExit(1)
                    dirs = sorted(root_dir.glob(mkdocs_path))
                    if dirs:
                        value = []
                        for mkdocs_config in dirs:
                            site = {}
                            try:
                                with open(mkdocs_config, 'rb') as f:
                                    site_yaml = yaml_load(f)
                                    site_name = site_yaml["site_name"]
                                site[site_name] = f"{INCLUDE_STATEMENT}{mkdocs_config.resolve()}"
                                value.append(site)
                            except OSError:
                                log.error(f"[mkdocs-monorepo] The {mkdocs_config} path is not valid.")
                            except KeyError:
                                log.critical(
                                    "[mkdocs-monorepo] The file path {} does not contain a valid 'site_name' key ".format(mkdocs_config) +
                                    "in the YAML file. Please include it to indicate where your documentation " +
                                    "should be moved to."
                                )
                                raise SystemExit(1)
                        if not value:
                            return None
                    else:
                        return None
            else:
                key = None
                value = None

            if type(value) is str and value.startswith(INCLUDE_STATEMENT):
                nav[index] = {}
                nav[index][key] = IncludeNavLoader(
                    self.config,
                    value[len(INCLUDE_STATEMENT):]
                ).read().getNav()

                if nav[index][key] is None:
                    return None
            elif type(value) is list:
                nav[index] = {}
                nav[index][key] = self.resolve(value)

                if nav[index][key] is None:
                    return None

        return nav


class IncludeNavLoader:
    def __init__(self, config, navPath):
        self.rootDir = os.path.normpath(os.path.join(
            os.getcwd(), config['config_file_path'], '../'))
        self.navPath = navPath
        self.absNavPath = os.path.normpath(
            os.path.join(self.rootDir, self.navPath))
        self.navYaml = None

    def getAbsNavPath(self):
        return self.absNavPath

    def read(self):
        if not self.absNavPath.endswith(tuple([".yml", ".yaml"])):
            log.critical(
                "[mkdocs-monorepo] The included file path {} does not point to a .yml (or .yaml) file".format(
                    self.absNavPath)
            )
            raise SystemExit(1)

        if not self.absNavPath.startswith(self.rootDir):
            log.critical(
                "[mkdocs-monorepo] The mkdocs file {} is outside of the current directory. ".format(self.absNavPath) +
                "Please move the file and try again."
            )
            raise SystemExit(1)

        try:
            with open(self.absNavPath, 'rb') as f:
                self.navYaml = yaml_load(f)

            # This will check if there is a `docs_dir` property on the `mkdocs.yml` file of
            # the sub folder and scaffold the `nav` property from it
            if self.navYaml and 'nav' not in self.navYaml:
                docsDir = self.navYaml.get("docs_dir", "docs")
                docsDirPath = os.path.join(os.path.dirname(self.absNavPath), docsDir)

                def navFromDir(path):
                    directory = {}

                    for dirname, dirnames, filenames in os.walk(path):

                        dirnames.sort()
                        filenames.sort()

                        if dirname == docsDirPath:
                            dn = os.path.basename(dirname)
                        else:
                            dn = dirname_to_title(os.path.basename(dirname))
                        directory[dn] = []

                        for dirItem in dirnames:
                            subNav = navFromDir(path=os.path.join(path, dirItem))
                            if subNav:
                                directory[dn].append(subNav)

                        for fileItem in filenames:
                            fileName, fileExt = os.path.splitext(fileItem)
                            if fileExt == '.md':
                                fileTitle = get_markdown_title(fileName)
                                filePath = os.path.join(os.path.relpath(path, docsDirPath), fileItem)
                                directory[dn].append({fileTitle: filePath})

                        if len(directory[dn]) == 0 or directory[dn] == [{}]:
                            del directory[dn]

                        return directory

                navYaml = navFromDir(docsDirPath)
                if navYaml:
                    self.navYaml["nav"] = navYaml[os.path.basename(docsDirPath)]

        except OSError:
            log.critical(
                "[mkdocs-monorepo] The file path {} does not exist, ".format(self.absNavPath) +
                "is not valid YAML, " +
                "or does not contain a valid 'site_name' and 'nav' keys."
            )
            raise SystemExit(1)

        if self.navYaml and 'site_name' not in self.navYaml:
            log.critical(
                "[mkdocs-monorepo] The file path {} does not contain a valid 'site_name' key ".format(self.absNavPath) +
                "in the YAML file. Please include it to indicate where your documentation " +
                "should be moved to."
            )
            raise SystemExit(1)

        if self.navYaml and 'nav' not in self.navYaml:
            log.critical(
                "[mkdocs-monorepo] The file path {} ".format(self.absNavPath) +
                "does not contain a valid 'nav' key in the YAML file " +
                "and the docs folder is not the default one, i.e. `docs`. " +
                "Please include the `nav` key to indicate how your documentation should be presented in the navigation, " +
                "or include a 'docs_dir' to indicate that automatic nav generation should be used."
            )
            raise SystemExit(1)

        return self

    def getDocsDir(self):
        return self.navYaml.get("docs_dir", "docs")

    def getAlias(self):
        alias = self.navYaml["site_name"]
        regex = '^[a-zA-Z0-9_\-/]+$'  # noqa: W605

        if re.match(regex, alias) is None:
            alias = slugify(self.navYaml["site_name"])

        return alias

    def getNav(self):
        return self._prependAliasToNavLinks(self.getAlias(), self.navYaml["nav"])

    def _prependAliasToNavLinks(self, alias, nav):
        for index, item in enumerate(nav):
            if type(item) is str:
                key = None
                value = item
            elif type(item) is dict:
                key = list(item.keys())[0]
                value = list(item.values())[0]
            else:
                key = None
                value = None

            if type(value) == str:
                nav[index] = {}

                if value.startswith(INCLUDE_STATEMENT):
                    log.critical(
                        "[mkdocs-monorepo] We currently do not support nested !include statements inside of Mkdocs.")
                    raise SystemExit(1)

                def formatNavLink(alias, value):
                    scheme, netloc, path, query, fragment = urlsplit(value)
                    # true if the value is an absolute link
                    if scheme or netloc:
                        return "{}".format(value)
                    else:
                        return "{}/{}".format(alias, value)

                if key is None:
                    nav[index] = formatNavLink(alias, value)
                else:
                    nav[index][key] = formatNavLink(alias, value)

            elif type(value) == list:
                nav[index] = {}
                nav[index][key] = self._prependAliasToNavLinks(alias, value)

        return nav

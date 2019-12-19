# Copyright 2019 Spotify AB
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

from mkdocs.utils import yaml_load, warning_filter

log = logging.getLogger(__name__)
log.addFilter(warning_filter)

INCLUDE_STATEMENT = "!include "


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
            else:
                value = None

            if type(value) is str and value.startswith(INCLUDE_STATEMENT):
                paths.append(value[len(INCLUDE_STATEMENT):])
            elif type(value) is list:
                paths.extend(self.__loadAliasesAndResolvedPaths(value))

        return paths

    def getResolvedPaths(self):
        def removeMkdocsYmlFromPath(path):
            rootDir = os.path.normpath(os.path.join(
                os.getcwd(), self.config['config_file_path'], '../'))
            absPath = os.path.normpath(os.path.join(
                rootDir, re.sub(r'\/mkdocs.yml$', '', path, re.IGNORECASE)))
            return absPath

        def extractAliasAndPath(absPath):
            return [IncludeNavLoader(self.config, absPath).read().getAlias(), removeMkdocsYmlFromPath(absPath)]

        resolvedPaths = list(
            map(extractAliasAndPath, self.__loadAliasesAndResolvedPaths()))

        for alias, resolvedPath in resolvedPaths:
            if not os.path.exists(resolvedPath):
                log.critical(
                    "[mkdocs-monorepo] The {} path is not valid. ".format(resolvedPath) +
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
        if not self.absNavPath.endswith("mkdocs.yml"):
            log.critical(
                "[mkdocs-monorepo] The included file path {} does not point to a mkdocs.yml".format(
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
                "does not contain a valid 'nav' key in the YAML file. " +
                "Please include it to indicate how your documentation should be presented in the navigation."
            )
            raise SystemExit(1)

        return self

    def getAlias(self):
        alias = self.navYaml["site_name"]
        regex = '^[a-zA-Z0-9_\-/]+$'  # noqa: W605

        if re.match(regex, alias) is None:
            log.critical(
                "[mkdocs-monorepo] Site name can only contain letters, numbers, underscores, hyphens and forward-slashes. " +
                "The regular expression we test against is '{}'.".format(regex))
            raise SystemExit(1)

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

                if key is None:
                    nav[index] = "{}/{}".format(alias, value)
                else:
                    nav[index][key] = "{}/{}".format(alias, value)

            elif type(value) == list:
                nav[index] = {}
                nav[index][key] = self._prependAliasToNavLinks(alias, value)

        return nav

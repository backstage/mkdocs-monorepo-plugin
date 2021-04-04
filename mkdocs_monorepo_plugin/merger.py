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

from tempfile import TemporaryDirectory
from distutils.dir_util import copy_tree

import logging
import os
from os.path import join
from pathlib import Path

from mkdocs.utils import yaml_load, warning_filter

log = logging.getLogger(__name__)
log.addFilter(warning_filter)

# This collects the multiple docs/ folders and merges them together.


class Merger:
    def __init__(self, config):
        self.config = config
        self.root_docs_dir = config['docs_dir']
        self.docs_dirs = list()
        self.append('', self.root_docs_dir)
        self.files_source_dir = dict()

    def append(self, alias, docs_dir):
        self.docs_dirs.append([alias, docs_dir])

    def merge(self):
        self.temp_docs_dir = TemporaryDirectory('', 'docs_')

        aliases = list(filter(lambda docs_dir: len(docs_dir) > 0, map(
            lambda docs_dir: docs_dir[0], self.docs_dirs)))
        if len(aliases) != len(set(aliases)):
            log.critical(
                "[mkdocs-monorepo] You cannot have duplicated site names. " +
                "Current registered site names in the monorepository: {}".format(', '.join(aliases)))
            raise SystemExit(1)

        for alias, docs_dir in self.docs_dirs:
            if len(alias) == 0:
                source_dir = docs_dir
                dest_dir = self.temp_docs_dir.name
            else:
                config_file = os.path.join(docs_dir, 'mkdocs.yml')
                if not os.path.exists(config_file):
                    log.critical(
                        "[mkdocs-monorepo] The {} path is not valid. ".format(config_file) +
                        "Please update your 'nav' with a valid path.")
                    raise SystemExit(1)
                try:
                    with open(config_file, 'rb') as f:
                        config_yaml = yaml_load(f)
                except OSError:
                    log.critical(
                        "[mkdocs-monorepo] The file path {} does not exist, ".format(self.absNavPath) +
                        "or is not valid YAML.")
                    raise SystemExit(1)

                subdocs_dir = config_yaml.get('docs_dir', 'docs')
                source_dir = os.path.join(docs_dir, subdocs_dir)
                split_alias = alias.split("/")
                dest_dir = os.path.join(self.temp_docs_dir.name, *split_alias)

            if os.path.exists(source_dir):
                copy_tree(source_dir, dest_dir)
                for file_abs_path in Path(source_dir).rglob('*.md'):
                    file_abs_path = str(file_abs_path) # python 3.5 compatibility
                    if os.path.isfile(file_abs_path):
                        file_rel_path = os.path.relpath(file_abs_path, source_dir)
                        dest = join(dest_dir, file_rel_path)
                        self.files_source_dir[dest] = file_abs_path

            else:
                log.critical(
                    "[mkdocs-monorepo] The {} path is not valid. ".format(source_dir) +
                    "Please update your 'nav' with a valid path.")
                raise SystemExit(1)

        return str(self.temp_docs_dir.name)

    def getFilesSourceFolder(self):
        return self.files_source_dir

    def cleanup(self):
        return self.temp_docs_dir.cleanup()

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

from mkdocs.plugins import BasePlugin
from .parser import Parser
from .merger import Merger


class MonorepoPlugin(BasePlugin):
    def __init__(self):
        self.parser = None
        self.merger = None
        self.originalDocsDir = None
        self.resolvedPaths = []
        self.files_source_dir = {}

    def on_config(self, config):
        # If no 'nav' defined, we don't need to run.
        if not config.get('nav'):
            return config

        # Handle !import statements
        self.parser = Parser(config)
        resolvedNav = self.parser.resolve()
        resolvedPaths = self.parser.getResolvedPaths()

        config['nav'] = resolvedNav

        # Generate a new "docs" directory
        self.merger = Merger(config)
        for alias, docs_dir, yaml_file in resolvedPaths:
            self.merger.append(alias, docs_dir)
        new_docs_dir = self.merger.merge()

        # Update the docs_dir with our temporary one!
        self.originalDocsDir = config['docs_dir']
        config['docs_dir'] = new_docs_dir

        # Store resolved paths for later.
        self.resolvedPaths = resolvedPaths

        # Store source directory of copied files for later
        self.files_source_dir = self.merger.getFilesSourceFolder()

        return config

    def on_pre_page(self, page, config, files):
        # Update page source attribute to point to source file
        # Only in case any files were moved.
        if len(self.files_source_dir) > 0:
            if page.file.abs_src_path in self.files_source_dir:
                page.file.abs_src_path = self.files_source_dir[page.file.abs_src_path]
        return page

    def on_serve(self, server, config, **kwargs):
        # Support mkdocs < 1.2
        if hasattr(server, 'watcher'):
            buildfunc = list(server.watcher._tasks.values())[0]['func']

            # still watch the original docs/ directory
            server.watch(self.originalDocsDir, buildfunc)

            # watch all the sub docs/ folders
            for _, docs_dir, yaml_file in self.resolvedPaths:
                server.watch(yaml_file, buildfunc)
                server.watch(docs_dir, buildfunc)
        else:
            # still watch the original docs/ directory
            server.watch(self.originalDocsDir)

            # watch all the sub docs/ folders
            for _, docs_dir, yaml_file in self.resolvedPaths:
                server.watch(yaml_file)
                server.watch(docs_dir)

    def post_build(self, config):
        self.merger.cleanup()

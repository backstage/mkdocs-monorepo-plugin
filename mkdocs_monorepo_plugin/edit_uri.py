# Copyright 2022 Spotify AB
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

from mkdocs.utils import yaml_load
from os import path

class EditUrl:
  def __init__(self, config, page, plugin):
      self.config = config
      self.page = page
      self.plugin = plugin

  def __get_root_config_file_path(self):
    return path.dirname(self.config['config_file_path'])

  def __get_root_docs_dir(self):
    abs_root_config_file_dir = self.__get_root_config_file_path()
    return path.relpath(self.plugin.originalDocsDir, abs_root_config_file_dir)

  def __get_page_dir_alias(self):
    parts = self.page.url.split('/')
    while True:
      parts.pop()
      alias = path.join(*parts)
      if alias in self.plugin.aliases:
        return alias

  def __get_page_docs_dir(self):
    alias = self.__get_page_dir_alias()
    abs_root_config_file_dir = self.__get_root_config_file_path()
    abs_page_config_file_dir = self.plugin.aliases[alias]['docs_dir']
    return path.relpath(abs_page_config_file_dir, abs_root_config_file_dir)

  def __get_page_src_path(self):
    alias = self.page.url.split('/')[0]
    path = self.page.file.src_path
    return path.replace('{}/'.format(alias), '')

  def __get_page_config_file_path(self):
    alias = self.__get_page_dir_alias()
    return self.plugin.aliases[alias]['yaml_file']

  def __load_page_config_file(self, file):
    config = yaml_load(file)

    root_docs_dir = self.__get_root_docs_dir()
    root_repo_url = self.config.get('repo_url')
    root_edit_uri = self.config.get('edit_uri', '')

    page_docs_dir = self.__get_page_docs_dir()
    page_repo_url = config.get('repo_url', root_repo_url)
    page_edit_uri = config.get('edit_uri', root_edit_uri.replace(root_docs_dir, page_docs_dir))

    # ensure a well-formed edit_uri
    if page_edit_uri:
      if not page_edit_uri.startswith(('?', '#')) \
        and not page_repo_url.endswith('/'):
          page_repo_url += '/'
      if not page_edit_uri.endswith('/'):
        page_edit_uri += '/'

    config['docs_dir'] = page_docs_dir
    config['edit_uri'] = page_edit_uri
    config['repo_url'] = page_repo_url

    return config

  def __get_page_config_file_yaml(self):
    abs_page_config_file_path = self.__get_page_config_file_path()
    with open(abs_page_config_file_path, 'rb') as f:
      return self.__load_page_config_file(f)

  def __has_repo(self):
    page_config_file_yaml = self.__get_page_config_file_yaml()
    return bool(page_config_file_yaml.get('repo_url'))

  def __is_root(self):
    root_config_docs_dir = self.__get_root_docs_dir()
    abs_root_config_file_dir = self.__get_root_config_file_path()
    abs_root_config_docs_dir = path.join(abs_root_config_file_dir, root_config_docs_dir)

    return path.realpath(abs_root_config_docs_dir) in self.page.file.abs_src_path

  def build(self):
    if self.__is_root():
      return self.page.edit_url
    if self.__has_repo():
      config = self.__get_page_config_file_yaml()
      return config['repo_url'] + config['edit_uri'] + self.__get_page_src_path()
    return None

def set_edit_url(config, page, plugin):
  edit_url = EditUrl(config, page, plugin)
  page.edit_url = edit_url.build()

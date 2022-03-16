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

from urllib.parse import urlsplit

def load_mkdocs_config(file, docs_dir):
  config = yaml_load(file)

  repo_url = config.get('repo_url')
  repo_name = config.get('repo_name')
  edit_uri = config.get('edit_uri')

  # derive repo_name from repo_url if unset
  if repo_url is not None and repo_name is None:
    repo_host = urlsplit(repo_url).netloc.lower()
    if repo_host == 'github.com':
      repo_name = 'GitHub'
    elif repo_host == 'bitbucket.org':
      repo_name = 'Bitbucket'
    elif repo_host == 'gitlab.com':
      repo_name = 'GitLab'
    else:
      repo_name = repo_host.split('.')[0].title()

  # derive edit_uri from repo_name if unset
  if repo_name is not None and edit_uri is None:
    if repo_name == 'GitHub' or repo_name == 'GitLab':
      edit_uri = 'edit/master/docs/{}'.format(docs_dir)
    elif repo_name == 'Bitbucket':
      edit_uri = 'src/default/docs/{}'.format(docs_dir)
    else:
      edit_uri = ''

  # ensure a well-formed edit_uri
  if edit_uri:
    if not edit_uri.startswith(('?', '#')) \
      and not config['repo_url'].endswith('/'):
        config['repo_url'] += '/'
    if not edit_uri.endswith('/'):
      edit_uri += '/'

  config['docs_dir'] = docs_dir
  config['edit_uri'] = edit_uri
  config['repo_name'] = repo_name

  return config

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

  def __get_page_config_file_yaml(self):
    page_docs_dir = self.__get_page_docs_dir()
    abs_page_config_file_path = self.__get_page_config_file_path()
    with open(abs_page_config_file_path, 'rb') as f:
      return load_mkdocs_config(f, page_docs_dir)

  def __has_repo(self):
    page_config_file_yaml = self.__get_page_config_file_yaml()
    return 'repo_url' in page_config_file_yaml

  def __is_root(self):
    root_config_docs_dir = self.__get_root_docs_dir()
    abs_root_config_file_dir = self.__get_root_config_file_path()
    abs_root_config_docs_dir = path.join(abs_root_config_file_dir, root_config_docs_dir)
    return abs_root_config_docs_dir in self.page.file.abs_src_path

  def build(self):
    if self.__is_root():
      return self.page.edit_url
    if self.__has_repo():
      config = self.__get_page_config_file_yaml()
      self.config['repo_name'] = config['repo_name']
      return config['repo_url'] + config['edit_uri'] + self.__get_page_src_path()
    return ''
    
def set_edit_url(config, page, plugin):
  edit_url = EditUrl(config, page, plugin)
  page.edit_url = edit_url.build()


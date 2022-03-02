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
from os import path, sep

def normalize(path):
  normalized = path
  if path.startswith('/'):
    normalized = normalized[1:]
  if not path.endswith('/'):
    normalized = '{}/'.format(path)
  return normalized

def get_root_config_dir_head(config, plugin):
  abs_root_config_file_dir = path.dirname(config['config_file_path'])
  return path.relpath(plugin.originalDocsDir, abs_root_config_file_dir)

def get_page_config_dir_head(config, page):
  abs_root_config_file_dir = path.dirname(config['config_file_path'])
  rel_page_markdown_file_path = path.relpath(page.file.abs_src_path, abs_root_config_file_dir)
  return rel_page_markdown_file_path.split(sep)[0]

def get_page_config_file_dir(config, page):
  abs_root_config_file_dir = path.dirname(config['config_file_path'])
  page_config_dir_head = get_page_config_dir_head(config, page)
  return path.join(abs_root_config_file_dir, page_config_dir_head)

def get_page_config_file_path(config, page):
  abs_page_config_file_dir = get_page_config_file_dir(config, page)
  abs_page_config_file_path = path.join(abs_page_config_file_dir, 'mkdocs.yaml')
  if not path.exists(abs_page_config_file_path):
    abs_page_config_file_path = path.join(abs_page_config_file_dir, 'mkdocs.yml')
  return abs_page_config_file_path

def get_page_config_file_yaml(config, page):
  abs_page_config_file_path = get_page_config_file_path(config, page)
  with open(abs_page_config_file_path, 'rb') as f:
    return { 'docs_dir': 'docs', **yaml_load(f) }

def replace_page_repo_url(config, page):
  page_config_file_yaml = get_page_config_file_yaml(config, page)
  if 'repo_url' in page_config_file_yaml:
    page_config_repo_url = normalize(page_config_file_yaml['repo_url'])
    page.edit_url = page.edit_url.replace(config['repo_url'], page_config_repo_url)

def replace_page_docs_dir(config, page, plugin):
  root_config_dir_head = get_root_config_dir_head(config, plugin)
  page_config_dir_head = get_page_config_dir_head(config, page)
  page_config_file_yaml = get_page_config_file_yaml(config, page)
  page_config_docs_dir = page_config_file_yaml['docs_dir']

  root_docs_dir_text = '/{}/'.format(root_config_dir_head)
  page_docs_dir_text = '/{}/{}/'.format(page_config_dir_head, page_config_docs_dir)

  page.edit_url = page.edit_url.replace(root_docs_dir_text, page_docs_dir_text)

def replace_page_edit_uri(config, page, plugin):
  page_config_file_yaml = get_page_config_file_yaml(config, page)
  if 'edit_uri' in page_config_file_yaml:
    page_config_edit_uri = normalize(page_config_file_yaml['edit_uri'])
    page.edit_url = page.edit_url.replace(config['edit_uri'], page_config_edit_uri)
  else:
    replace_page_docs_dir(config, page, plugin)

def replace_page_dir_alias(page):
  page_docs_dir_alias = page.url.split('/')[0]
  page_docs_dir_alias_text = '/{}'.format(page_docs_dir_alias)
  page.edit_url = page.edit_url.replace(page_docs_dir_alias_text, '')

def is_index(page):
  return len(page.url) == 0

def set_edit_url(config, page, plugin):
  if page.edit_url is not None:
    replace_page_dir_alias(page)
    replace_page_repo_url(config, page)
    replace_page_edit_uri(config, page, plugin)

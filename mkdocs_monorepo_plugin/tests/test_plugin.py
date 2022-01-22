#!/usr/bin/env python

import unittest
from mkdocs_monorepo_plugin import plugin as p


class MockServer():
    """MockServer tracks what the livereload.Server instance is watching."""

    def __init__(self):
        self.watched = []

    def watch(self, input):
        self.watched.append(input)


class TestMonorepoPlugin(unittest.TestCase):
    def test_plugin_on_config_defaults(self):
        plugin = p.MonorepoPlugin()
        plugin.on_config({})
        self.assertIsNone(plugin.originalDocsDir)

    def test_plugin_on_config_with_nav(self):
        plugin = p.MonorepoPlugin()
        plugin.on_config({
                    "nav": {"page1": "page1.md"},
                    "docs_dir": "docs"
                })
        self.assertEqual(plugin.originalDocsDir, "docs")

    def test_plugin_on_serve_no_run(self):
        plugin = p.MonorepoPlugin()
        plugin.originalDocsDir = None
        server = MockServer()
        plugin.on_serve(server, {})
        self.assertEqual(server.watched, [])

    def test_plugin_on_serve(self):
        plugin = p.MonorepoPlugin()
        plugin.originalDocsDir = "docs"
        plugin.resolvedPaths = []
        server = MockServer()
        plugin.on_serve(server, {})
        self.assertSetEqual(set(server.watched), {
            "docs"
            })

# Philosophy

This plugin is designed to solve documentation in **large codebases** &mdash; whether monorepos, monoliths or sizeable codebases in general &mdash; by enabling [Mkdocs] to be split out into smaller documentation folders. Then when shipping a change to production, merge the documentation together into a single, digestable site.

Typically, in these large codebases, there is often complex ownership. Teams may own folders, files, or even parts of a single file. This localizes documentation to the code so it can seamlessly inherit ownership strategies designed for code, such as [GitHub Codeowners].

It was originally designed to improve the documentation process in Spotify's critical software, some which are monoliths with complex ownership across many teams, offices, and continents.

[mkdocs]: https://www.mkdocs.org
[github codeowners]: https://help.github.com/en/articles/about-code-owners
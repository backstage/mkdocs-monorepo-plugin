# Caveats / Known Design Decisions

- In an included `mkdocs.yml`, you cannot have `!include`. It is only supported in the root `mkdocs.yml`
- In an included `mkdocs.yml`, your `site_name` must adhere follow the regular expression: `^[a-zA-Z0-9_\-/]+$`
- In an included `mkdocs.yml`, it currently looks for the relative `docs/` folder and does not respect the `docs_dir` value.

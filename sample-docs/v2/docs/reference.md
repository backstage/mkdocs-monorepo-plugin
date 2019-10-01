# v2 API reference

This contains the v2 API reference.

## GET /v2/cats

Returns a list of all cats.

## GET /v2/breeds

Returns a list of all breeds of cats.

## GET /v2/breeds/:breed_name/cats

Returns a list of all cats under the `:breed_name` breed.

## GET /v2/search

Parameters:

- `q` = A string containing the search query for a cat name or breed.

Returns a list of cats that match the search query.

- Markdown source: `sample-docs/v2/docs/reference.md`
- Permalink: <https://spotify.github.io/mkdocs-monorepo-plugin/monorepo-example/versions/v2/reference/>
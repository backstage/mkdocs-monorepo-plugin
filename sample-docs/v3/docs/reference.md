# v3 API reference

This contains the v3 API reference.

## GET /v3/cats

Returns a list of all cats.

## GET /v3/breeds

Returns a list of all breeds of cats.

## GET /v3/breeds/:breed_name/cats

Returns a list of all cats under the `:breed_name` breed.

## GET /v3/search

Parameters:

- `q` = A string containing the search query for a cat name or breed.

Returns a list of cats that match the search query.

- Markdown source: `sample-docs/v3/docs/reference.md`
- Permalink: <https://spotify.github.io/mkdocs-monorepo-plugin/monorepo-example/versions/v3/reference/>

## GET /v3/cat/:name/lives_left

Returns how many lives the cat named `:name` still has left.
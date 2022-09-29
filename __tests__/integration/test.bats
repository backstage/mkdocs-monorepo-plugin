##
# Install the mkdocs-monorepo-plugin locally on test run.
#
pip install -e . --quiet >&2

##
# These are helper variables and functions written in Bash. It's like writing in your Terminal!
# Feel free to optimize these, or even run them in your own Terminal.
#

rootDir=$(pwd)
fixturesDir=${rootDir}/__tests__/integration/fixtures

debugger() {
  echo "--- STATUS ---"
  if [ $status -eq 0 ]
  then
    echo "Successful Status Code ($status)"
  else
    echo "Failed Status Code ($status)"
  fi
  echo "--- OUTPUT ---"
  echo $output
  echo "--------------"
}

assertFileExists() {
  run cat $1
  [ "$status" -eq 0 ]
}

assertFileContains() {
  run grep $2 $1
  [ "$status" -eq 0 ]
}

assertFileNotContains() {
  run grep $2 $1
  [ "$status" -eq 1 ]
}

assertSuccessMkdocs() {
  run mkdocs $@
  debugger
  assertFileExists site/index.html
  [ "$status" -eq 0 ]
}

assertFailedMkdocs() {
  run mkdocs $@
  debugger
  [ "$status" -ne 0 ]
}

##
# These are special lifecycle methods for Bats (Bash automated testing).
# setup() is ran before every test, teardown() is ran after every test.
#

teardown() {
  rm -rf ${fixturesDir}/**/*/site
}

##
# Test suites.
#

@test "builds a mkdocs site with minimal configuration" {
  cd ${fixturesDir}/ok-vanilla
  assertSuccessMkdocs build
}

@test "builds a mkdocs site from a different folder" {
  cd ${fixturesDir}
  run mkdocs build --config-file=ok-conflict/mkdocs.yml
  debugger
  run cat ok-conflict/site/index.html
  [[ "$output" == *"Lorem markdownum aequora Famemque"* ]]
  run cat ok-conflict/site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok/project-a fixture."* ]]
}


@test "builds a mkdocs site with the correct contents and paths" {
  cd ${fixturesDir}/ok-conflict
  assertSuccessMkdocs build
  run cat site/index.html
  [[ "$output" == *"Lorem markdownum aequora Famemque"* ]]
  run cat site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok/project-a fixture."* ]]
}

@test "builds a mkdocs site with single !include" {
  cd ${fixturesDir}/ok
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok/project-a fixture."* ]]
}

@test "builds a mkdocs site inside a nested mkdocs.yml" {
  cd ${fixturesDir}/ok/project-a
  assertSuccessMkdocs build
  [[ "$output" == *"This contains a sentence which only exists in the ok/project-a fixture."* ]]
}

@test "builds a mkdocs site with no nav and no docs_dir key" {
  cd ${fixturesDir}/ok-no-nav-no-dir
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok/project-a fixture."* ]]
}

@test "builds a mkdocs site with yaml extension" {
  cd ${fixturesDir}/ok-yaml-not-yml
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-yaml-not-yml fixture."* ]]
}

@test "builds a mkdocs site if !include path does not contain nav" {
  cd ${fixturesDir}/ok-include-path-no-nav
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-include-path-no-nav/project-a fixture."* ]]
  # Check if directory names are formatted correctly
  [[ "$output" == *"Small small"* ]]
  # Check if Title names are generated correctly by using the markdown header
  [[ "$output" == *"OkIncludePathNoNavProjectATestPage"* ]]
}

@test "builds a mkdocs site with docs_dir differently specified in mkdocs.yml" {
  cd ${fixturesDir}/ok-different-docs-dir
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-different-docs-dir/project-a fixture."* ]]
}

@test "builds a mkdocs site with different config file than mkdocs.yml" {
  cd ${fixturesDir}/ok-different-config-name
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-different-config-name/project-a fixture."* ]]
}

@test "builds a mkdocs site with site_name containing slash" {
  cd ${fixturesDir}/ok-nested-site-name-contains-slash
  assertSuccessMkdocs build
  assertFileExists site/plugins/example-Folder/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-nested-site-name-contains-slash/project-a fixture."* ]]
}

@test "builds a mkdocs site with mkdocs-git-authors-plugin" {
  cd ${fixturesDir}/ok-git-authors-plugin
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-git-authors-plugin/project-a fixture."* ]]
}

@test "builds a mkdocs site with mkdocs-git-revision-date-localized-plugin" {
  cd ${fixturesDir}/ok-mkdocs-git-revision-date-localized-plugin
  assertSuccessMkdocs build
  assertFileExists site/test/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-mkdocs-git-revision-date-localized-plugin/project-a fixture."* ]]
}

@test "builds a mkdocs even if !include path has site_name containing spaces" {
  cd ${fixturesDir}/ok-include-path-site-name-contains-space
  assertSuccessMkdocs build
}

@test "builds a mkdocs site with single *include" {
  cd ${fixturesDir}/ok-include-wildcard
  assertSuccessMkdocs build
  assertFileExists site/test-a/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-include-wildcard/project-a fixture."* ]]
  assertFileExists site/test-b/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-include-wildcard/project-b fixture."* ]]
}

@test "builds a mkdocs site with recursive *include" {
  cd ${fixturesDir}/ok-include-wildcard-recursive-glob
  assertSuccessMkdocs build
  assertFileExists site/test-a/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-include-wildcard-recursive-glob/projects/project-a fixture."* ]]
  assertFileExists site/test-c/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-include-wildcard-recursive-glob/projects/subprojects/project-c fixture."* ]]
}

@test "builds a mkdocs site from a different folder with wildcard include" {
  cd ${fixturesDir}
  run mkdocs build --config-file=ok-include-wildcard/mkdocs.yml
  debugger
  run cat ok-include-wildcard/site/index.html
  [[ "$output" == *"Lorem markdownum aequora Famemque"* ]]
  run cat ok-include-wildcard/site/test-a/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-include-wildcard/project-a fixture."* ]]
  run cat ok-include-wildcard/site/test-b/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-include-wildcard/project-b fixture."* ]]
}

@test "fails if !include path is above current folder" {
  cd ${fixturesDir}/error-include-path-is-parent
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The mkdocs file "*"/__tests__/integration/fixtures/mkdocs.yml is outside of the current directory. Please move the file and try again."* ]]
}

@test "fails if !include path contains !include" {
  cd ${fixturesDir}/error-include-path-contains-include
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] We currently do not support nested !include statements inside of Mkdocs."* ]]
}

@test "fails if !include paths contains duplicate site_name values" {
  cd ${fixturesDir}/error-include-paths-duplicate-site-name
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] You cannot have duplicated site names. Current registered site names in the monorepository: test, test"* ]]
}

@test "fails if !include path does not exist" {
  cd ${fixturesDir}/error-include-path-not-found
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The file path /"*"/__tests__/integration/fixtures/error-include-path-not-found/project-a/mkdocs.yml does not exist, is not valid YAML, or does not contain a valid 'site_name' and 'nav' keys."* ]]
}

@test "fails if !include path does not contain site_name" {
  cd ${fixturesDir}/error-include-path-no-site-name
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The file path /"*"/__tests__/integration/fixtures/error-include-path-no-site-name/project-a/mkdocs.yml does not contain a valid 'site_name' key in the YAML file. Please include it to indicate where your documentation should be moved to."* ]]
}

@test "fails if !include path does not contain docs/ folder" {
  cd ${fixturesDir}/error-include-path-no-docs-folder
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The /"*"/__tests__/integration/fixtures/error-include-path-no-docs-folder/project-a/docs path is not valid. Please update your 'nav' with a valid path."* ]]
}

@test "fails if absolute links aren't supported" {
  cd ${fixturesDir}/include-path-absolute-url
  assertSuccessMkdocs build

  assertFileContains './site/index.html' 'href="http://www.absoluteurl.nl"'
  assertFileContains './site/index.html' 'href="https://www.absoluteurl.nl/sub/dir"'
  assertFileContains './site/index.html' 'href="ftp://ftp.absoluteurl.nl"'

  assertFileContains './site/index.html' 'href="ftp://ftp.absoluteurl-root.nl"'

  [ "$status" -eq 0 ]
}

@test "fails if *include path does not end in yml or yaml" {
  cd ${fixturesDir}/error-include-wildcard-not-yml
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The wildcard include path ./projects/*/mkdocs.txt does not end with .yml (or .yaml)"* ]]
}

@test "fails if !include path from a wildcard include does not contain site_name" {
  cd ${fixturesDir}/error-include-wildcard-no-site-name
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The file path /"*"/__tests__/integration/fixtures/error-include-wildcard-no-site-name/projects/project-a/mkdocs.yml does not contain a valid 'site_name' key in the YAML file. Please include it to indicate where your documentation should be moved to."* ]]
}

@test "sets edit url for included path pages" {
  cd ${fixturesDir}/ok-include-path-edit-uri
  assertSuccessMkdocs build

  assertFileContains './site/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-edit-uri/docs/index.md"'
  assertFileContains './site/test/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-edit-uri/api/docs/index.md"'
  assertFileContains './site/test/other/other/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-edit-uri/api/docs/other/other.md"'
}

@test "sets edit url for included wildcard pages" {
  cd ${fixturesDir}/ok-include-wildcard-edit-uri
  assertSuccessMkdocs build

  assertFileContains './site/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-edit-uri/docs/index.md"'
  assertFileContains './site/test/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-edit-uri/projects/api/docs/index.md"'
  assertFileContains './site/test/other/other/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-edit-uri/projects/api/docs/other/other.md"'
}

@test "derive edit_uri from root for included paths" {
  cd ${fixturesDir}/ok-include-path-no-edit-uri
  assertSuccessMkdocs build

  assertFileContains './site/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-no-edit-uri/docs/index.md"'
  assertFileContains './site/test/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-no-edit-uri/api/docs/index.md"'
  assertFileContains './site/test/other/other/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-no-edit-uri/api/docs/other/other.md"'
}

@test "derive edit_uri from root for wildcard paths" {
  cd ${fixturesDir}/ok-include-wildcard-no-edit-uri
  assertSuccessMkdocs build

  assertFileContains './site/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-no-edit-uri/docs/index.md"'
  assertFileContains './site/test/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-no-edit-uri/projects/api/docs/index.md"'
  assertFileContains './site/test/other/other/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-no-edit-uri/projects/api/docs/other/other.md"'
}

@test "does not default to root edit_uri if it is not configured" {
  cd ${fixturesDir}/ok-include-path-no-repo-url
  assertSuccessMkdocs build

  assertFileNotContains './site/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-no-repo-url/docs/index.md"'
  assertFileNotContains './site/test/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-no-repo-url/api/docs/index.md"'
  assertFileNotContains './site/test/other/other/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-path-no-repo-url/api/docs/other/other.md"'
}

@test "does not default to root edit_uri if it is not configured for wildcard paths" {
  cd ${fixturesDir}/ok-include-wildcard-no-repo-url
  assertSuccessMkdocs build

  assertFileNotContains './site/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-no-repo-url/docs/index.md"'
  assertFileNotContains './site/test/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-no-repo-url/projects/api/docs/index.md"'
  assertFileNotContains './site/test/other/other/index.html' 'href="https://github.com/backstage/mkdocs-monorepo-plugin/edit/master/__tests__/integration/fixtures/ok-include-wildcard-no-repo-url/projects/api/docs/other/other.md"'
}


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

@test "builds a mkdocs site with site_name containing slash" {
  cd ${fixturesDir}/ok-nested-site-name-contains-slash
  assertSuccessMkdocs build
  assertFileExists site/plugins/example-Folder/index.html
  [[ "$output" == *"This contains a sentence which only exists in the ok-nested-site-name-contains-slash/project-a fixture."* ]]
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

@test "fails if !include path has site_name containing spaces" {
  cd ${fixturesDir}/error-include-path-site-name-contains-space
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] Site name can only contain letters, numbers, underscores, hyphens and forward-slashes. The regular expression we test against is '^[a-zA-Z0-9_\-/]+$'."* ]]
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

@test "fails if !include path does not contain nav" {
  cd ${fixturesDir}/error-include-path-no-nav
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The file path /"*"/__tests__/integration/fixtures/error-include-path-no-nav/project-a/mkdocs.yml does not contain a valid 'nav' key in the YAML file. Please include it to indicate how your documentation should be presented in the navigation."* ]]
}

@test "fails if !include path does not contain docs/ folder" {
  cd ${fixturesDir}/error-include-path-no-docs-folder
  assertFailedMkdocs build
  [[ "$output" == *"[mkdocs-monorepo] The /"*"/__tests__/integration/fixtures/error-include-path-no-docs-folder/project-a/docs path is not valid. Please update your 'nav' with a valid path."* ]]
}

@test "fails if !include paths included yml has an absolute url. Which results in a broken url" {
  cd ${fixturesDir}/include-path-absolute-url
  assertSuccessMkdocs build

  assertFileContains './site/index.html' 'href="http://www.absoluteurl.nl"'
  assertFileContains './site/index.html' 'href="https://www.absoluteurl.nl"'
  # "{}/{}".format(alias, value) in parser.py results in 	'href="test/ftp://ftp.not-supported-absoluteurl.nl"'
  # resulting test/index.html shows 						'href="test/ftp:/ftp.not-supported-absoluteurl.nl"'  though
  # resulting ./index.html shows 							'href="test/ftp://ftp.not-supported-absoluteurl.nl"'
  # looks like monorepo somehow changes the link. i.e. a slash is lost!
  assertFileContains './site/index.html' 'href="test/ftp:/ftp.not-supported-absoluteurl.nl"'
  assertFileContains './site/index.html' 'href="test/x http:/www.not-supported-absoluteurl.nl"'

  # root included links really stay untouched. In the root actually every protocol is supported because refences stay untouched
  assertFileContains './site/index.html' 'href="ftp://ftp.not-supported-absoluteurl-in-root.nl"'

  [ "$status" -eq 0 ]
}

# Changelog

## v2.4.0 (2024-01-15)

### Feature

- check provided email address with pyisemail

### Fix

- remove unnecessary markdown message in request field

### Style

- fix run-on sentence

### Chores/Misc

- add build section to read the docs config
- add regex for version line in citation file
- add citation.cff to list of files with version
- add contributing guidelines
- add code of conduct
- add citation file
- update support.md links

## v2.3.1 (2023-07-17)

### Docs

- update logos

## v2.3.0 (2023-04-11)

### Feature

- add a prefix to email subject when it's provided in the config
- allow users to specify a subject line in their contact emails

### Fix

- expect no trailing space in the prefix from config

### Refactor

- move tests into unit subdir

### Docs

- add the new prefix option to the docs

### Tests

- fix a test
- add additional tests for the ne subject changes

### Build System(s)

- fix postgres not loading when running tests in docker

### Chores/Misc

- add action to sync branches when commits are pushed to main

## v2.2.0 (2023-04-03)

### Feature

- allow contact emails to be sent to multiple recipients

## v2.1.6 (2023-02-20)

### Docs

- fix api docs generation script

### Style

- reformat with prettier

### Chores/Misc

- small fixes to align with other extensions

## v2.1.5 (2023-01-31)

### Docs

- **readme**: change logo url from blob to raw

## v2.1.4 (2023-01-31)

### Docs

- **readme**: direct link to logo in readme
- **readme**: fix github actions badge

## v2.1.3 (2023-01-30)

### Build System(s)

- **docker**: use 'latest' tag for test docker image

## v2.1.2 (2022-12-12)

### Style

- change quotes in setup.py to single quotes

### Build System(s)

- include any top-level data files in theme
- add package data

## v2.1.1 (2022-12-01)

### Docs

- **readme**: fix table borders
- **readme**: format test section
- **readme**: update ckan patch version in header badge
- **readme**: update installation steps

## v2.1.0 (2022-11-28)

### Docs

- fix markdown-include references
- add section delimiters

### Style

- apply formatting changes

### Build System(s)

- set changelog generation to incremental
- pin minor version of ckantools
- add include-markdown plugin to mkdocs

### CI System(s)

- add cz_nhm dependency in bump workflow
- **commitizen**: fix message template
- add pypi release action

### Chores/Misc

- use cz_nhm commitizen config
- improve commitizen message template
- standardise package files

## v2.0.1 (2022-09-20)

## v2.0.0 (2021-03-09)

## v1.0.0-alpha (2019-07-23)

## v0.0.3 (2019-05-01)

## v0.0.2 (2018-05-10)

## v0.0.1 (2016-01-19)

# Changelog

All notable changes to this project will be documented in this file.

## [0.3.2] - 2026-09-12

### Miscellaneous Tasks
- *Ci*: Move from dependabot to renovate
- *Dependencies*: Bump cems-nuclei to 3.2.1 to allow new access tokens

### Testing
- *Sound*: Fix mask to check that row is string before splitting in test_get_normative_building

## [0.3.1] - 2025-04-22

### Bug Fixes
- *Dependencies*: Add fiona dependency to fix SBR notebook

## [0.3.0] - 2025-04-22

### Bug Fixes
- *Ci*: Use proper upload artifact version

### Documentation
- *Changelog*: Remove custom changelog format

### Refactor
- *Python*:  [**BREAKING**]Set minimum supported python version to 3.11 and support 3.13

## [0.2.1] - 2024-07-25

### Bug Fixes
- *SBR*: Paging wfs query
- *SBRb*: Change A3 values for day 3 and 4

### Miscellaneous Tasks

- *SBR*:
    - Update notebook add matplotlib widget
    - Use Line2D in plot legend
    - Relocated referenceLocation to CUR codeblock

## [0.2.0] - 2024-06-21

### Bug Fixes
- Update notebook SBR; add `to_csv` for all dataframes
- Reduce vibration velocity with reliability index
- Update logic for building plot

### Documentation
- Use more descriptive attribute names

### Features
- *Sbr-b*: Allow multi building validation
- Add SBR-B to notebook
- Initial setup SBR-B

## [0.1.7] - 2024-03-19

### Features
- Allow optional plot settings

## [0.1.6] - 2024-03-19

### Features
- Allow optional plot settings

## [0.1.5] - 2024-03-15

### Bug Fixes
- Better error massage handling

### Features
- Add allow groundwater_level_offset to be set for project

## [0.1.4] - 2024-02-14

### Bug Fixes
- *Constants*: Update SOIL REFERENCE properties

## [0.1.3] - 2024-02-13

### Bug Fixes
- *Ci*: Use PyPi tokenless authentication
- *Constants*: Update SOIL REFERENCE properties
- *Plot*: Update legend of vibration prediction reduction plot

### Documentation
- Update comments in notebook

### Styling
- Format markdown and bash file

## [0.1.2] - 2023-12-21

### Bug Fixes
- *Notebook*: Add arguments to call endpoint method
- *Plot*: Update color of the input building settings figure
- Use get methode to obtain data

### Documentation
- Add docstring sound calculation
- Add function reference and user guide

### Refactor
- Move measurement_type parameter
- Move measurement_type and methode_safety_factor

## [0.1.1] - 2023-11-14

### Bug Fixes
- Update sound prediction function

## [0.0.1] - 2023-11-13

### Documentation
- Add reference to docs

### Features
- *Sound*: Add sound prediction

### Miscellaneous Tasks
- *Notebook*: Update notebook
- Update gitignore
- Remove fig save
- Silence SettingWithCopyWarning
- Init commit py-vibracore

### Styling
- Lint code with black isort and mypy

<!-- CEMS BV. -->

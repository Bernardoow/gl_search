# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2022-10-28

### Added

- Add logic to skip search at repository after retries when happen http status code 429.

### Changed

- Change to use session.get instead of request.get.
- Add Retry to HttpStatus response 429, 502, 503 and 504.

## [0.3.0] - 2022-10-22

### Added

- User view feedback.
- Optional debug param.

### Changed

- Change from 20 to 100 results at search in repositories.

## [0.2.0] - 2022-10-20

### Added

- Add optional max-delay-request param to search command.

## [0.1.0] - 2022-10-15

### Added

- Add search command
- Add token config command
- Add gitlab address command

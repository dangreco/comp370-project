# COMP 370 Project

<!-- markdownlint-disable line-length  -->

[![Nix](https://github.com/dangreco/comp370-project/actions/workflows/nix.yml/badge.svg)](https://github.com/dangreco/comp370-project/actions/workflows/nix.yml) [![CI](https://github.com/dangreco/comp370-project/actions/workflows/ci.yml/badge.svg)](https://github.com/dangreco/comp370-project/actions/workflows/ci.yml) [![CD](https://github.com/dangreco/comp370-project/actions/workflows/cd.yml/badge.svg)](https://github.com/dangreco/comp370-project/actions/workflows/cd.yml)

<!-- markdownlint-enable line-length  -->

## Description

A Seinfeld script analysis application that scrapes episode data from the Internet
Movie Script Database (IMSDB) and provides a GraphQL API for querying episode scripts,
characters, writers, and metadata.

### Features

- **Web Scraper**: Automated scraper for collecting Seinfeld episode data including:
  - Episode titles and air dates
  - Full episode scripts with character dialogue
  - Writer credits
  - Season organization

- **GraphQL API**: Query interface for accessing the scraped data with support for:
  - Episode metadata queries
  - Script and dialogue searches
  - Character and writer information
  - Interactive GraphiQL playground

- **Data Persistence**: SQLAlchemy-based database for storing and
  querying episode data

- **HTTP Caching**: Request caching to minimize load on the source website
  and improve performance

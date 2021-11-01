# Ransomwatch-rss-api

## Goal

Provides an RSS interface to the Ransomwatch project.

Please note that this piece of code does not gather any data from any platform, it only exposes results on a RSS feed fashion. 

## Installation

1. `git clone` the repository in the same parent directory as of ransomwatch (the same sqlite db will be used): 
```.
├── ransomwatch
│   └── db_vol
│       └── ransomwatch.db
├── ransomwatch-rss-api
│   ├── api
│   ├── README.md
│   └── docker-compose.yml
```
2. get into the ransomwatch-rss-api directory
1. run the `docker-compose build` command

## Usage

Once the build has completed you can start the API by running `docker-compose up`. It will listen on port 8080 as specified in the docker-compose.yml configuration file.

If you have entries in the ransomwatch.db sqlite database, you can already configure your RSS software to reach `http://localhost/rss` and enjoy the results.

## Documentation 

Swagger auto-generated documentation is available at: http://localhost:8080/docs

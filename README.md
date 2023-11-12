# API Server for BudgetKey

This server contains the two main api servers for the BudgetKey website.

It makes use of these libraries:
- [APISQL](https://github.com/dataspot/apisql), for providing a read only query API to a DBMS
- [APIES](https://github.com/OpenBudget/apies), for providing a read only search and fetch API to an ElasticSearch instance
- [AUTH](://github.com/dataspot/dgp-oauth2), for providing authentication and authorization to the API endpoints

## Routes

TBD

(for specific enpoints see the respective library documentation)

## Serving

This image uses gunicorn for web serving.

It uses multiple workers and listens on port 5000.

## Configuration

All configuration is done via environment variables:
- Auth:
    - DATABASE_URL - the URL to the database to use for read/write queries
    - PRIVATE_KEY - the private key to use for signing JWT tokens
    - PUBLIC_KEY - the public key to use for verifying JWT tokens
    - GOOGLE_KEY - the Google API key to use for Google authentication
    - GOOGLE_SECRET - the Google API secret to use for Google authentication
    - GITHUB_KEY - the Github API key to use for Github authentication
    - GITHUB_SECRET - the Github API secret to use for Github authentication
- Querying:
    - DATABASE_READONLY_URL - the URL to the database to use for read only queries
- ElasticSearch:
    - ES_HOST - the host of the ElasticSearch instance to use
    - ES_PORT - the port of the ElasticSearch instance to use
    - INDEX_NAME - the name of the ElasticSearch index to use
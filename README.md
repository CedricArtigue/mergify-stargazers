<p align="center">
  <a href="" rel="noopener">
 <img src="./logo.png" alt="Project logo"></a>
</p>
<h3 align="center">Mergify Stargazers Case</h3>

## 💡 TODO <a name = "todo"></a>
- setup unit test on usecases, injecting mockedup services and repositories
- setup ci to run unit tests
- setup ci to run integration tests (it will be a little bit longer)
- include a database ?
- setup github flow in CI ?

## 📝 Table of Contents

- [💡 TODO ](#-todo-)
- [📝 Table of Contents](#-table-of-contents)
- [🧐 Problem Statement ](#-problem-statement-)
- [💡 Idea / Solution ](#-idea--solution-)
- [⛓️ Dependencies / Limitations ](#️-dependencies--limitations-)
- [🏁 Getting Started ](#-getting-started-)
- [🎈 Usage ](#-usage-)
- [🚀 Future Scope ](#-future-scope-)

## 🧐 Problem Statement <a name = "problem_statement"></a>

The goal of this project is to have a web service that can receive such a request:
```
GET /repos/<user>/<repo>/starneighbours
```
This endpoint must return the list of neighbours github repositories, meaning repositories where at least one stargazer is found in common.
The returned JSON format should look like:
```json
[
 {
   "repo": <repoA>,
    "stargazers": [<stargazers in common>, ...],
 },
 ...
]
```

## 💡 Idea / Solution <a name = "idea"></a>

Tools we'll be using:
- FastAPI framework to develop the API
- pandas library for fast data analysis and manipulation
- docker to run the api
- docker-compose to easily setup the required stack
- a FastAPI template repository

Github API provides endpoints to
- fetch stargazers of a specific (owner/repo) tuple 
- fetch starred repositories of a specific stargazer

We'll setup the required API endpoint to which tied up business logic will be in charge of:
- authenticating incoming client calls using FastAPI OAuth2PasswordBearer method
- fetching stargazers of a specific repo
- fetch starred repo of each previous stargazers
- build a pandas dataframe holding those data
- run some pandas data preparation on top of it \(filtering, grouping and formatting result)
- send formatted data to the client

## ⛓️ Dependencies / Limitations <a name = "limitations"></a>
Depending on the target repository the number of stargazers can be huge. 

At first look (I may be wrong), it seems that we cannot read starred repositories for a list of users in the same Github API call, which means that we must call Github API as many time as there is stargazers on the target repository (and this stands true ONLY if we have a single stargazers or starred repositories page for each endpoint, which won't hold for long)

On the other hand, Github API is rate limited as follow:
- 60 api hits per hour for non authenticated users
- 5000 api hits per hour for authenticated users

For the sake of simplicity and dev rapidity, during the first naive approach we'll limit ourselves to a maximum of less than 60 api calls for building the required result, which translates to:
- a single stargazers page for a target repo will be fetched
- only a single page of starred repository will be fecthed only for a few stargazers.

We'll comment later in this document how we can alleviate those limitations (db, queue, checkpoint restart, etc)

## 🏁 Getting Started <a name = "getting_started"></a>

The only requirements to develop are a running Docker engine and Make.

To start up the project locally you first clone the project, and then run the following command in the cloned directory:

```shell
git clone https://github.com/CedricArtigue/mergify-stargazers.git
cd mergify-stargazers
make up
```

## 🎈 Usage <a name="usage"></a>

The integrated swagger gui allows to easily test the authenticated API endpoints.

After running previous step, app should be running at [localhost:5000](http://localhost:5000).

Authenticate with dummy user (no database for now):
- login: johndoe
- password: secret 


## 🚀 Future Scope <a name = "future_scope"></a>

TODO
<p align="center">
  <a href="" rel="noopener">
 <img src="./logo.png" alt="Project logo"></a>
</p>
<h3 align="center">Mergify Stargazers Case</h3>

## 📝 Table of Contents

- [📝 Table of Contents](#-table-of-contents)
- [🧐 Problem ](#-problem-)
  - [statement](#statement)
  - [limitations](#limitations)
- [💡 First Solution and Future Scope](#-first-solution-and-future-scope)
  - [Architecture](#architecture)
  - [Stack and Services](#stack-and-services)
  - [Scalability](#scalability)
    - [Data structure](#data-structure)
    - [Rate limitation](#rate-limitation)
    - [Load Balancing and Database Race conditions](#load-balancing-and-database-race-conditions)
- [🏁 Getting Started ](#-getting-started-)
- [🎈 Usage ](#-usage-)
- [🏁 Tests ](#-tests-)
- [🚀 Future Scope ](#-future-scope-)

## 🧐 Problem <a name = "problem_statement"></a>
### statement
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

### limitations
Depending on the target repository the number of stargazers can be huge. 

At first look (I may be wrong), it seems that we cannot read starred repositories for a list of users in the same Github API call, which means that we must call Github API as many time as there is stargazers on the target repository (and this stands true ONLY if we have a single stargazers or starred repositories page for each endpoint, which won't hold for long)

On the other hand, Github API is rate limited as follow:
- 60 api hits per hour for non authenticated users
- 5000 api hits per hour for authenticated users

For the sake of simplicity and dev rapidity, during the first naive approach we'll limit ourselves to a maximum of less than 60 api calls for building the required result, which translates to:
- a single stargazers page for a target repo will be fetched
- only a single page of starred repository will be fetched only for a few stargazers.

## 💡 First Solution and Future Scope<a name = "solution"></a>
### Architecture

To improve readability, maintainability and testability, we'll be using tactical architectural patterns originated from clean architecture and solid principles
- Layered architecture:
  - domain layer: entities, domain errors, services/repositories interfaces
  - usecases layer: application-specific business rules
  - interface_adapters: in charge of implementing domain interfaces
  - infrastructure layer: database client/migrations, external services implementation (github service)
  - tests layer (not a real layer): api integration tests and unit tests (which directory structure mimics the app one) 
- Dependency Inversion Principle: basically here we are injecting infra dependencies into usecases, it allows decoupled unit testing of usecases while providing an ability to modify said dependencies implementation without breaking things 
- other patterns can be found, I'll be glad to discuss about it (Repo pattern, entities/aggregates, Domain Errors handling, single responsability, etc)

### Stack and Services
What we'll be using:
- docker to run the api
- docker-compose to easily setup the required stack
- FastAPI framework to develop the API
- FastAPI template repository (no need to reinvent the wheel for the case)
- Swagger UI: documents API and allow user to test it 
- FastAPI OAuth2PasswordBearer for authentication (mocked user database for now)
- Pandas library for fast data analysis and manipulation (highly efficient data structures)
- Github API to
  - fetch stargazers of a specific (owner/repo) tuple 
  - fetch starred repositories of a specific stargazer
- a postgresql database is included in the template, I did not use it yet, maybe later
- Pytest for unit and integration tests
- Makefile for build and tests scripts

### Scalability
#### Data structure
Pandas is highly memory efficient but as stated above, stargazers of repo can be a huge number and github API rate limitation can hit hard. For the sake of simplicity we are capping for now the number of API hits to demonstrate the feasibility and setup the complete app. 

#### Rate limitation
In real life, we must improve quite a lot the current implemented approach. We could:
- batch and queue stargazers' starred repo fetching and processing to prevent app to reach rate limit issue. We could have an advanced database data structure to allow asynchronous update of a specific repo starneighbours
- use multiple authenticated github account and a flee of agent in charge of running computations in parallel, with a master process in charge of reducing the global result
- decouple data ingestion from github API, and target data format restitution
- etc...

#### Load Balancing and Database Race conditions
One more thing would be about real usage of this app endpoints. If this app becomes a banger, in production we should have a scalable infrastructure to handle the love.
We should probably deploy the containerized app in a dedicated cluster with a load balancer dispatching the traffic accross multiple instances of the app.
As the application become parallel, and PostgreSQL is not, we should take extra precautions to prevent race conditions between app instances, namely using database transactions when data is saved in repositories. A great pattern we could use is the AggregateRoot one originated from DDD, with its corresponding tactical Repository pattern.
Used cleverly, those patterns neglect database race conditions by design.

## 🏁 Getting Started <a name = "getting_started"></a>

The following procedure has only been tested on macOS.
The only requirements to develop are a running Docker engine and Make (and a mac computer)

To start up the project locally you first clone the project, and then run the following command in the cloned directory:

```shell
git clone https://github.com/CedricArtigue/mergify-stargazers.git
cd mergify-stargazers
make up
```

## 🎈 Usage <a name="usage"></a>

The integrated swagger gui allows to easily test the authenticated API endpoints. After running previous step, app should be running at [localhost:5000](http://localhost:5000).

Authenticate with dummy user (no database for now), use Authorize Button on top of UI:
- login: johndoe
- password: secret 

Verify that you are logged in, with route
```
GET /users/me
```

Finally you can test the target endpoint, providing user/name repo paramaters
```
GET /repos/<user>/<repo>/starneighbours
```


## 🏁 Tests <a name = "tests"></a>

The tests are containerized and the Docker setup can be found in the .ci/ folder. They are written using Pytest. You can run the tests using:

```shell
make test
```

This runs the integration & unit tests. If you want to run them separately, use make itest to run the integration tests and make utest to run the unit tests.

## 🚀 Future Scope <a name = "future_scope"></a>
- implement persistence using postgre database
- Queue and batch global process to prevent github rate limiting issues
- include Github Auth in environment to decrease Rate Limitation pressure
- collaborative flow, enforce build/test/deployment in CI/CD (github actions)
- enforce coding style using a linter connected to a CI/CD job
- deploy application on a cloud service for staging purpose
- use a dedicated dependency injection library, and apply DIP to all usecases, making the code base more uniform
- remove template dead code about todos :)
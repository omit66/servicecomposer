# Service Composer
This tool intends to help running services from several git repositories.

Solving Tasks:
- collecting the services by cloning the git repos
- merging the docker compose files
- running the services

The tool enables to composing your service from serveral git repos with ease.
Do the configuration just once for each service and place at the root of
its git repository. Use this tool to merge the docker-compose and
start service without lookup the parameters and configs:)

Change the working machine and run the same services with just two command.

## services.yaml
Config file containing all services.
Each having a url to the corresponding git repository.

The structure is shown in the following example:
``
<Servicename>:
    url: <git-repo-url>
...
``

## Usage

Use the `init` command to initalize the repo.
Download the newest version of the services and merges the docker-compose files.

The command `run` starts all services or a specific service. This is just
`docker-compose up`.

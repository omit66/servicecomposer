import click

from . import composer


@click.group()
def main():
    pass


@click.command()
@click.option("--clone_dir", default="./clones/")
def init(clone_dir):
    """Initialize the repository for docker compose."""
    click.echo("Init Repo")
    composer.init(clone_dir)


@click.command()
def clean():
    """Stop and remove all created docker containers"""
    click.echo("Clean up docker containers...")
    composer.clean()


@click.command()
@click.option("-g", "--group", help="Use the name of a git repo to call all "
              "originated services.")
@click.argument('args', nargs=-1)
def run(group, args):
    """Run Services using docker-compose."""
    click.echo("Run Services (calling docker-compose up)...")
    composer.run(group, args)


main.add_command(init)
main.add_command(run)
main.add_command(clean)


if __name__ == "__main__":
    main()

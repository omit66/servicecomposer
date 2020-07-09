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
@click.argument('args', nargs=-1)
def run(args):
    click.echo("Run Services (calling docker-compose up)...")
    composer.run(args)


main.add_command(init)
main.add_command(run)


if __name__ == "__main__":
    main()

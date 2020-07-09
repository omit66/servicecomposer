import collections.abc
import io
import os

import click
import git
import yaml


def merge_dicts(d, u):
    """Merge two dictionary.
    If the value is not a mapping, then it is replaced.
    This function calls itself, whenever a values is a dictionary.
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = merge_dicts(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def adjust_rel_path(path, prefix):
    """Apply the prefix for the relativ pathes.
    Return the unchanged path, if the path is absolute or the new path does
    not exist."""
    result = path
    if not os.path.isabs(path):
        new_path = os.path.relpath(os.path.join(prefix, path))
        # if the does not exist we do nothing. There are three cases:
        # - path was already fixed and therefore cannot be found
        # - it is a url for a git repo
        # - the original path is broken
        if os.path.exists(new_path):
            # docker wants the relpath to start with a dot
            result = os.path.join('.', new_path)
    return result


def adjust_build(build, prefix):
    if isinstance(build, str):
        return adjust_rel_path(build, prefix)
    else:
        if "context" in build:
            build['context'] = adjust_rel_path(build['context'], prefix)
    return build


def adjust_volumes(volumes, prefix):
    new_volumes = []
    for v in volumes:
        parts = v.split(":")
        new_parts = []
        # the first two parts are pathes
        for p in parts[:2]:
            new_parts.append(adjust_rel_path(p, prefix))

        # append the options
        if len(parts) == 3:
            new_parts.append(parts[2])
        new_volumes.append(":".join(new_parts))
    return new_volumes


def run(group, args):
    """Run docker-compose"""
    compose_file = find_compose_file('.')
    if compose_file is None:
        click.echo("The file docker-compose.yml was not found. Did you run "
                   "'servicecomposer init'?")
        return
    import subprocess
    cmd = "docker-compose up".split()
    if group is not None:
        services = []
        for key in compose_file['services']:
            if key.startswith(group):
                services.append(key)
        cmd.extend(services)

    if args is not None:
        cmd.extend(args)
    click.echo(" ".join(cmd))
    subprocess.Popen(cmd)


def download_service_repository(url, target):
    """Download the newest service repository."""
    if not os.path.exists(target):
        click.echo("git clone %s" % url)
        git.Repo.clone_from(url, target)
    else:
        click.echo("git pull %s" % url)
        git.Repo(target).remote().pull()


def find_compose_file(path):
    """Find the docker compose file.
    It is checked for the extension .yaml and .yml.
    The corresponding dict is returned or None.

    Keyword Arguments:
    path -- dir to check for the files
    """
    yaml_ext = ['yml', 'yaml']
    filename = "docker-compose"
    for ext in yaml_ext:
        name = os.path.join(path, ".".join((filename, ext)))
        if os.path.exists(name):
            with io.open(name, "r") as f:
                return yaml.load(f)
    return None


def write_compose_file(data):
    compose_filename = "docker-compose.yaml"
    click.echo("Writing file {}".format(compose_filename))
    with io.open(compose_filename, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def init(clone_dir):
    """Initialize the repository for docker compose.
    - git clone/pull
    - merging docker-compose files
    """
    with io.open('services.yaml') as f:
        services = yaml.load(f)

    if not os.path.exists(clone_dir):
        os.mkdir(clone_dir)

    compose_file = find_compose_file(".") or {}

    for svc, data in services.items():
        repo_dir = os.path.join(clone_dir, svc)
        download_service_repository(data['url'], repo_dir)

        svc_compose = find_compose_file(repo_dir)
        if svc_compose is None:
            click.secho("No docker-compose file found at {}".format(repo_dir),
                        fg="yellow")
            # skip service
            continue

        click.secho("Services are renamed. This might fail!", fg="yellow")
        # adapt rel paths
        for name, service_content in svc_compose["services"].items():
            if "volumes" in service_content:
                service_content["volumes"] = adjust_volumes(
                        service_content['volumes'], repo_dir)
            if "build" in service_content:
                service_content["build"] = adjust_build(
                        service_content["build"], repo_dir)
            if "services" in svc_compose:
                data = svc_compose["services"]
                """
                if name in data:
                    # rename the service; may work in some case, but
                    # container_name is not change and the references to the
                    # host name.
                    # Furhter, calling init twice will lead to two entries for
                    # the same service.
                    # FIXME!
                    click.secho("This is bad: Two services having the same "
                                "name ({})".format(name), fg="yellow")
                """
                # rename each service for now...
                new_name = "{}_{}".format(svc, name)
                data[new_name] = data[name]
                # click.secho("Service is renamed to {}. Check the config! "
                #            "This might fail!".format(new_name),
                #            fg="yellow")
                del data[name]
                svc_compose["services"] = data

        # todo checks before overriding
        merge_dicts(compose_file, svc_compose)
    write_compose_file(compose_file)

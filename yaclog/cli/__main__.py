#  yaclog: yet another changelog tool
#  Copyright (c) 2021. Andrew Cassidy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import os.path

import click
import git

import yaclog.version
from yaclog.changelog import Changelog


@click.group()
@click.option('--path', envvar='YACLOG_PATH', default='CHANGELOG.md', show_default=True,
              type=click.Path(dir_okay=False, writable=True, readable=True),
              help='Location of the changelog file.')
@click.version_option()
@click.pass_context
def cli(ctx, path):
    """Manipulate markdown changelog files."""
    if not (ctx.invoked_subcommand == 'init') and not os.path.exists(path):
        # file does not exist and this isn't the init command
        raise click.FileError(f'Changelog file {path} does not exist. Create it by running `yaclog init`.')

    ctx.obj = yaclog.read(path)


@cli.command()
@click.pass_obj
def init(obj: Changelog):
    """Create a new changelog file."""
    if os.path.exists(obj.path):
        click.confirm(f'Changelog file {obj.path} already exists. Would you like to overwrite it?', abort=True)
        os.remove(obj.path)

    yaclog.Changelog(obj.path).write()
    print(f'Created new changelog file at {obj.path}')


@cli.command('format')  # dont accidentally hide the `format` python builtin
@click.pass_obj
def reformat(obj: Changelog):
    """Reformat the changelog file."""
    obj.write()
    print(f'Reformatted changelog file at {obj.path}')


@cli.command(short_help='Show changes from the changelog file')
@click.option('--all', '-a', 'all_versions', is_flag=True, help='Show the entire changelog.')
@click.option('--markdown/--txt', '-m/-t', default=False, help='Display as markdown or plain text.')
@click.option('--full', '-f', 'str_func', flag_value=lambda v, k: v.text(**k), default=True,
              help='Show version header and body.')
@click.option('--name', '-n', 'str_func', flag_value=lambda v, k: v.name, help='Show only the version name')
@click.option('--body', '-b', 'str_func', flag_value=lambda v, k: v.body(**k), help='Show only the version body.')
@click.option('--header', '-h', 'str_func', flag_value=lambda v, k: v.header(**k), help='Show only the version header.')
@click.argument('version_names', metavar='VERSIONS', type=str, nargs=-1)
@click.pass_obj
def show(obj: Changelog, all_versions, markdown, str_func, version_names):
    """Show the changes for VERSIONS.

    VERSIONS is a list of versions to print. If not given, the most recent version is used.
    """

    try:
        if all_versions:
            versions = obj.versions
        elif len(version_names) == 0:
            versions = [obj.current_version()]
        else:
            versions = [obj.get_version(name) for name in version_names]
    except KeyError as k:
        raise click.BadArgumentUsage(k)
    except ValueError as v:
        raise click.ClickException(v)

    kwargs = {'md': markdown}

    for v in versions:
        text = str_func(v, kwargs)
        click.echo(text)
        click.echo('\n')


@cli.command(short_help='Modify version tags')
@click.option('--add/--delete', '-a/-d', default=True, is_flag=True, help='Add or delete tags')
@click.argument('tag_name', metavar='tag', type=str)
@click.argument('version_name', metavar='VERSION', type=str, required=False)
@click.pass_obj
def tag(obj: Changelog, add, tag_name: str, version_name: str):
    """Modify TAG on VERSION.

    VERSION is the name of a version to add tags to. If not given, the most recent version is used.
    """
    tag_name = tag_name.upper()
    try:
        if version_name:
            version = obj.get_version(version_name)
        else:
            version = obj.current_version()
    except KeyError as k:
        raise click.BadArgumentUsage(k)
    except ValueError as v:
        raise click.ClickException(v)

    if add:
        version.tags.append(tag_name)
    else:
        try:
            version.tags.remove(tag_name)
        except ValueError:
            raise click.BadArgumentUsage(f'Tag {tag_name} not found in version {version.name}.')

    obj.write()


@cli.command(short_help='Add entries to the changelog.')
@click.option('--bullet', '-b', 'bullets', multiple=True, type=str,
              help='Bullet points to add. '
                   'When multiple bullet points are provided, additional points are added as sub-points.')
@click.option('--paragraph', '-p', 'paragraphs', multiple=True, type=str,
              help='Paragraphs to add')
@click.argument('section_name', metavar='SECTION', type=str, default='', required=False)
@click.argument('version_name', metavar='VERSION', type=str, default=None, required=False)
@click.pass_obj
def entry(obj: Changelog, bullets, paragraphs, section_name, version_name):
    """Add entries to SECTION in VERSION

    SECTION is the name of the section to append to. If not given, entries will be uncategorized.

    VERSION is the name of the version to append to. If not given, the most recent version will be used,
    or a new 'Unreleased' version will be added if the most recent version has been released.
    """

    section_name = section_name.title()
    try:
        if version_name:
            version = obj.get_version(version_name)
        else:
            version = obj.current_version(released=False, new_version=True)
    except KeyError as k:
        raise click.BadArgumentUsage(k)

    for p in paragraphs:
        version.add_entry(p, section_name)

    for b in bullets:
        version.add_entry('- ' + b, section_name)

    obj.write()


@cli.command(short_help='Release versions.')
@click.option('-v', '--version', 'version_name', type=str, default=None, help='The new version number to use.')
@click.option('-M', '--major', 'rel_seg', flag_value=0, default=None, help='Increment major version number.')
@click.option('-m', '--minor', 'rel_seg', flag_value=1, help='Increment minor version number.')
@click.option('-p', '--patch', 'rel_seg', flag_value=2, help='Increment patch number.')
@click.option('-a', '--alpha', 'pre_seg', flag_value='a', default=None, help='Increment alpha version number.')
@click.option('-b', '--beta', 'pre_seg', flag_value='b', help='Increment beta version number.')
@click.option('-r', '--rc', 'pre_seg', flag_value='rc', help='Increment release candidate version number.')
@click.option('-f', '--full', 'pre_seg', flag_value='', help='Clear the prerelease value creating a full release.')
@click.option('-c', '--commit', is_flag=True,
              help='Create a git commit tagged with the new version number. '
                   'If there are no changes to commit, the current commit will be tagged instead.')
@click.pass_obj
def release(obj: Changelog, version_name, rel_seg, pre_seg, commit):
    """Release versions in the changelog and increment their version numbers"""

    cur_version = obj.current_version()
    old_name = cur_version.name

    if version_name:
        new_name = version_name
    else:
        for v in obj.versions:
            if v.version is not None:
                new_name = v.name
                break
        else:
            new_name = '0.0.0'

    if rel_seg is not None or pre_seg is not None:
        new_name = yaclog.version.increment_version(new_name, rel_seg, pre_seg)

    if new_name != old_name:
        if yaclog.version.is_release(old_name):
            click.confirm(f'Rename release version "{cur_version.name}" to "{new_name}"?', abort=True)

        cur_version.name = new_name
        cur_version.date = datetime.datetime.utcnow().date()

        obj.write()
        print(f'Renamed version "{old_name}" to "{cur_version.name}".')

    if commit:
        repo = git.Repo(os.curdir)

        if repo.bare:
            raise click.BadOptionUsage('commit', f'Directory {os.path.abspath(os.curdir)} is not a git repo.')

        repo.index.add(obj.path)

        version_type = '' if yaclog.version.is_release(cur_version.name) else 'non-release '
        tracked = len(repo.index.diff(repo.head.commit))
        tracked_warning = 'Create tag'
        untracked = len(repo.index.diff(None))
        untracked_warning = ''
        untracked_plural = 's' if untracked > 1 else ''
        if untracked > 0:
            untracked_warning = click.style(
                f' You have {untracked} untracked file{untracked_plural} that will not be included.',
                fg='red', bold=True)

        if tracked > 0:
            tracked_warning = 'Commit and create tag'

        click.confirm(f'{tracked_warning} for {version_type}version {cur_version.name}?{untracked_warning}',
                      abort=True)

        if tracked > 0:
            commit = repo.index.commit(f'Version {cur_version.name}\n\n{cur_version.body()}')
            print(f'Created commit {repo.head.commit.hexsha[0:7]}')
        else:
            commit = repo.head.commit

        repo_tag = repo.create_tag(cur_version.name, ref=commit, message=cur_version.body(False))
        print(f'Created tag "{repo_tag.name}".')


if __name__ == '__main__':
    cli()

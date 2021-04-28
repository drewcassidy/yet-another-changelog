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
import os
import re
from typing import List, Optional, Dict

import yaclog.markdown as markdown
import yaclog.version

default_header = '# Changelog\n\nAll notable changes to this project will be documented in this file'


class VersionEntry:
    """Holds a single version entry in a :py:class:`Changelog`"""

    def __init__(self, name: str = 'Unreleased',
                 date: Optional[datetime.date] = None, tags: Optional[List[str]] = None,
                 link: Optional[str] = None, link_id: Optional[str] = None):
        """
        Create a new version entry

        :param str name: The version's name
        :param date: When the version was released
        :param tags: The version's tags
        :param link: The version's URL
        :param link_id: The version's link ID
        """

        self.name: str = name
        """The version's name"""

        self.date: Optional[datetime.date] = date
        """WHen the version was released"""

        self.tags: List[str] = tags if tags else []
        """The version's tags"""

        self.link: Optional[str] = link
        """The version's URL"""

        self.link_id: Optional[str] = link_id
        """The version's link ID, uses the version name by default when writing"""

        self.line_no: Optional[int] = None
        """What line the version occurs at in the file, or None if the version was not read from a file. 
        This is not guaranteed to be correct after the changelog has been modified, 
        and it has no effect on the written file"""

        self.sections: Dict[str, List[str]] = {'': []}
        """The dictionary of change entries in the version, organized by section. 
        Uncategorized changes have a section of an empty string."""

    def add_entry(self, contents: str, section: str = '') -> None:
        """
        Add a new entry to the version

        :param contents: The contents string to add
        :param section: Which section to add to.
        """

        section = section.title()
        if section not in self.sections.keys():
            self.sections[section] = []

        self.sections[section].append(contents)

    def body(self, md: bool = True) -> str:
        """
        Get the version's body as a string

        :param md: Whether or not to use markdown syntax in headings
        :return: The formatted version body, without the version header
        """

        segments = []

        for section, entries in self.sections.items():
            if section:
                if md:
                    segments.append(f'### {section.title()}')
                else:
                    segments.append(f'{section.upper()}:')

            if len(entries) > 0:
                segments += entries

        return markdown.join(segments)

    def header(self, md: bool = True) -> str:
        """
        Get the version's header as a string

        :param md: Whether or not to use markdown syntax in headings
        :return: The formatted version header
        """

        segments = []

        if md:
            segments.append('##')

        if self.link and md:
            segments.append(f'[{self.name}]')
        else:
            segments.append(self.name)

        if self.date or len(self.tags) > 0:
            segments.append('-')

        if self.date:
            segments.append(self.date.isoformat())

        segments += [f'[{t.upper()}]' for t in self.tags]

        return ' '.join(segments)

    def text(self, md: bool = True) -> str:
        """
        Get the version's contents as a string

        :param md: Whether or not to use markdown syntax in headings
        :return: The formatted version header and body
        """

        contents = self.header(md)
        body = self.body(md)
        if body:
            contents += '\n\n' + body
        return contents

    @property
    def released(self):
        return yaclog.version.is_release(self.name)

    def __str__(self) -> str:
        return self.header(False)


class Changelog:
    """A changelog made up of a header, several versions, and a link table"""

    def __init__(self, path=None, header: str = default_header):
        """
        Create a new changelog object. Contents will be automatically read from disk if the file exists

        :param path: The changelog's path on disk
        :param header: The header at the top of the changelog to use if the file does not exist
        """
        self.path = os.path.abspath(path) if path else None
        """The path of the changelog's file on disk"""

        self.header: str = header
        """Any text at the top of the changelog before any H2s"""

        self.versions: List[VersionEntry] = []
        """A list of versions in the changelog"""

        self.links = {}
        """Link IDs at the end of the changelog"""

        if path and os.path.exists(path):
            self.read()

    def read(self, path=None) -> None:
        """
        Read a markdown changelog file from disk

        :param path: The changelog's path on disk. By default, :py:attr:`~Changelog.path` is used.
        """

        if not path:
            # use the object path if none was provided
            path = self.path

        # Read file
        with open(path, 'r') as fp:
            tokens, self.links = markdown.tokenize(fp.read())

        section = ''
        header_segments = []

        for token in tokens:
            text = '\n'.join(token.lines)

            if token.kind == 'h2':
                # start of a version

                slug = text.rstrip('-').strip('#').strip()
                split = slug.split()
                if '-' in split:
                    split.remove('-')

                version = VersionEntry()
                section = ''

                version.name = slug
                version.line_no = token.line_no
                tags = []
                date = None

                for word in split[1:]:
                    if match := re.match(r'\d{4}-\d{2}-\d{2}', word):
                        # date
                        try:
                            date = datetime.date.fromisoformat(match[0])
                        except ValueError:
                            break
                    elif match := re.match(r'^\[(?P<tag>\S*)]', word):
                        tags.append(match['tag'])
                    else:
                        break

                else:
                    # matches the schema
                    version.name, version.link, version.link_id = markdown.strip_link(split[0])
                    version.date = date
                    version.tags = tags

                self.versions.append(version)

            elif len(self.versions) == 0:
                # we haven't encountered any version headers yet,
                # so its best to just add this line to the header string
                header_segments.append(text)

            elif token.kind == 'h3':
                # start of a version section
                section = text.strip('#').strip()
                if section not in self.versions[-1].sections.keys():
                    self.versions[-1].sections[section] = []

            else:
                # change log entry
                self.versions[-1].sections[section].append(text)

        # handle links
        for version in self.versions:
            if match := re.fullmatch(r'\[(.*)]', version.name):
                # ref-matched link
                link_id = match[1].lower()
                if link_id in self.links:
                    version.link = self.links[link_id]
                    version.link_id = None
                    version.name = match[1]

            elif version.link_id in self.links:
                # id-matched link
                version.link = self.links[version.link_id]

        # strip whitespace from header
        self.header = markdown.join(header_segments)

    def write(self, path: os.PathLike = None) -> None:
        """
        Write a markdown changelog to a file.

        :param path: The changelog's path on disk. By default, :py:attr:`~Changelog.path` is used.
        """

        if path is None:
            # use the object path if none was provided
            path = self.path

        segments = [self.header]
        v_links = {**self.links}

        for version in self.versions:
            if version.link:
                v_links[version.name.lower()] = version.link

            segments.append(version.text())

        segments += [f'[{link_id}]: {link}' for link_id, link in v_links.items()]

        text = markdown.join(segments)

        with open(path, 'w') as fp:
            fp.write(text)

    def add_version(self, index: int = 0, *args, **kwargs) -> VersionEntry:
        """
        Add a new version to the changelog

        :param index: Where to add the new version in the log. Defaults to the top
        :param args: args to forward to the :py:class:`VersionEntry` constructor
        :param kwargs: kwargs to forward to the :py:class:`VersionEntry` constructor
        :return: The created entry
        """
        self.versions.insert(index, version := VersionEntry(*args, **kwargs))
        return version

    def current_version(self, released: Optional[bool] = None,
                        new_version_name: str = 'Unreleased') -> Optional[VersionEntry]:
        """
        Get the current version entry from the changelog

        :param released: if the returned version should be a released version,
            an unreleased version, or ``None`` to return the most recent
        :param new_version_name: if unreleased versions are allowed, the name of
            the version to create if there are no matches
        :return: The current version matching the criteria, or None if only
            release versions are allowed and none are found.
        """

        if released is None:
            # return the first version, we dont care about release status
            if len(self.versions) > 0:
                return self.versions[0]
        else:
            # return the first version that matches `released`
            for version in self.versions:
                if version.released == released:
                    return version

        # fallback if none are found
        if released:
            return None
        else:
            return self.add_version(name=new_version_name)

    def get_version(self, name: Optional[str] = None) -> VersionEntry:
        """
        Get a version from the changelog

        :param name: The name of the version to get, or ``None`` to return the most recent
        :return: The first version with the selected name
        """

        for version in self.versions:
            if version.name == name or name is None:
                return version
        raise IndexError()

    def __getitem__(self, item: str) -> VersionEntry:
        return self.get_version(item)

    def __len__(self) -> int:
        return len(self.versions)

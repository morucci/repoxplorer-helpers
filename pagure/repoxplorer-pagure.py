#!/usr/bin/env python

# Copyright 2018, Red Hat
# Copyright 2018, Fabien Boucher
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import yaml
import argparse
import requests
import time


STARTURL = 'https://src.fedoraproject.org/api/0/projects?page=1'
LIMIT = 11


class HTTPSession(object):
    def __init__(self):
        self.session = requests.Session()

    def get(self, url):
        print("Getting resource %s ..." % url)
        ret = self.session.get(url)
        return ret.json()


parser = argparse.ArgumentParser(
    description='Pagure repoXplorer projects file helper')
parser.add_argument(
    '--output-path', type=str, default='./',
    help='yaml file path to register organization repositories details')
parser.add_argument(
    '--file-prefix', type=str, default='',
    help='file name prefix')

args = parser.parse_args()


if __name__ == "__main__":
    hs = HTTPSession()
    c_page = STARTURL
    page = 1
    struct = {'projects': {
                'Fedora Distgits': {
                    "repos": {},
                    "description":
                        "All repositories from src.fedoraproject.org",
                    }
                },
              'project-templates': {
                  'fedora-distgit': {
                      "branches": ["master", ],
                      "uri": "https://src.fedoraproject.org/rpms/%(name)s",
                      "gitweb":
                          ("https://src.fedoraproject.org/rpms/" +
                           "%(name)s/c/%%(sha)s"),
                      "release": [
                        {'name': 'Fedora 28', 'date': '2018-05-01'},
                        {'name': 'Fedora 27', 'date': '2017-11-14'},
                        {'name': 'Fedora 26', 'date': '2017-07-11'},
                        {'name': 'Fedora 25', 'date': '2016-11-22'}],
                       }
              }}

    while True:
        if page == LIMIT:
            break
        data = hs.get(c_page)
        time.sleep(0.5)
        results = data.get('projects', [])
        for repo in results:
            name = repo['name']
            if not repo['fullname'].startswith('rpms/'):
                continue
            struct['projects']['Fedora Distgits']['repos'].update(
                {name: {'template': 'fedora-distgit'}})
        if c_page == data['pagination']['last']:
            break
        c_page = data['pagination']['next']
        page += 1

    path = '%s%s.yaml' % (
        args.file_prefix, 'src.fedoraproject.org')

    if args.output_path:
        path = os.path.join(os.path.expanduser(args.output_path), path)

    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, 'w') as fd:
        fd.write(yaml.safe_dump(struct,
                                default_flow_style=False))

    print("Source repositories details has been written to %s" % path)

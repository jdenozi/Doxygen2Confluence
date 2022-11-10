#!/usr/bin/env python3
import argparse
import logging

import ConfluenceAPI
from IOStream import IOStream

iostream = IOStream(color=True)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="syncToConfluence")
    parser.add_argument('-i', '--input', help='Documentation html file')
    parser.add_argument('-n', '--name', help='Name of the documentation')
    parser.add_argument('-u', '--user', help='User name used for confluence connection')
    parser.add_argument('-p', '--password', help='Password used for confluence connection')
    parser.add_argument('-di', '--documentationId',
                        help='Doc key of the document. Association of id and categories key.')
    parser.add_argument('-ci', '--categoryId', help='Doc key of the document. Association of id and categories key.')
    parser.add_argument('-up', '--update', action='store_true', help='Update document.')
    parser.add_argument('-c', '--create', help='Create new document.')
    parser.add_argument('-d', '--details', action="store_true", help='Get repository details.')
    parser.add_argument('-v', '--verbose', action="store_true", help='Add more details.')
    parser.add_argument('-r', '--remove', action="store_true", help='Remove documentation on Confluence repository.')

    args = parser.parse_args()

    print("    Sync documentation with confluence begin")
    print("    ----------------------------------------")

    confluence_api = ConfluenceAPI.ConfluenceApi("http://confluence.innopsys.lan:8090")

    if args.verbose:
        VERBOSE = True
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    if args.details:
        confluence_api.get_directory_details()

    if args.update or args.create:

        if args.user is None or args.password is None:
            iostream.stderr("No connection information are provided")

        if args.input is None:
            iostream.stderr("No archive or directory given")

        if args.name is None:
            iostream.stderr("No documentation name given")

        documentation_name = args.name.replace(".", "_")
        zipFile = confluence_api.exist(args.input, documentation_name)

        if args.update:
            if confluence_api.check_if_dock_already_exist(documentation_name):
                documentation_key = confluence_api.get_documentation_id(documentation_name)
                confluence_api.update_documentation(documentation_key, zipFile, args.user, args.password)
            else:
                confluence_api.create_documentation(args.categoryId, zipFile, args.user, args.password)

        if args.create:
            if args.user is None or args.password is None:
                iostream.stderr("No connection information are provided")
            confluence_api.create_documentation(args.keyDoc, zipFile, args.user, args.password)

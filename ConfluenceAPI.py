#!/usr/bin/env python3

import base64
import os
import os.path
import pathlib
import shutil

import requests
from requests import Response
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from IOStream import IOStream, StreamType

COMPRESSION_EXT_SUPPORTED = [".zip", ".jar"]
iostream = IOStream(color=True)


def check_http_error(response: Response, successful_message: str = "Successful",
                     error_message: str = "Error"):
    """
    Decorator to check http response.
    :return:
    """
    if type(response) is not Response:
        iostream.stderr("Wrong response argument, should be a Response object")
    try:
        # If the response was successful, no Exception will be raised
        response.raise_for_status()

    except HTTPError as http_err:
        iostream.stdout(error_message)
        iostream.stderr(f'HTTP error occurred: {http_err}')

    else:
        iostream.stdout(successful_message)


class ConfluenceApi:
    """
    API for Javadocs, Doxygen and other HTML and Javascript based documentation synchronisation to Confluence.
    """

    def __init__(self, base_url: str, verbose: bool = False):
        self.repository_url = "/rest/docs/2.0/repository/"
        self.base_url = base_url
        self.documentation_file = None
        self.verbose = verbose

    @staticmethod
    def compress(archive_directory: str, documentation_name: str) -> str:
        """
        Compress the given directory into zip file.
        :param documentation_name:Name of the archive given.
        :param archive_directory: Path of the directory.
        :return: The name of the archive created from directory.
        """
        archive_name = os.path.join(os.path.split(archive_directory)[0], documentation_name + ".zip")
        iostream.stdout("Directory {}/ compression into {}".format(archive_directory, archive_name),
                        StreamType.TITLE)

        # If a documentation already exist, remove it
        if os.path.isfile(documentation_name):
            os.remove(os.path.join(os.getcwd(), documentation_name))

        shutil.make_archive(os.path.join(os.path.split(archive_directory)[0], documentation_name), 'zip',
                            archive_directory)

        iostream.stdout("Successful", StreamType.BASE)
        return archive_name

    def exist(self, directory_or_file: str, documentation_name: str) -> str:
        """
        Check if the given directory or file (archive) path exist.
        :param documentation_name: Name of the documentation you want
        :param directory_or_file: Path directory.
        :return: Return the name of the archive directory
        """
        iostream.stdout("Check file or dir ", StreamType.TITLE)

        # Compute the full path
        directory_or_file_path = os.path.join(os.getcwd(), directory_or_file)

        # Check if it's an archive file
        if os.path.isfile(directory_or_file_path):
            if pathlib.Path(directory_or_file_path).suffix not in COMPRESSION_EXT_SUPPORTED:
                iostream.stdout("Not ok")
                iostream.stdout("Documentation extension not supported (supported are " + "".join(
                    map(str, COMPRESSION_EXT_SUPPORTED)))
            else:
                iostream.stdout("Ok")
                return directory_or_file

        if os.path.isdir(directory_or_file_path):
            iostream.stdout("Ok")
            return self.compress(directory_or_file_path, documentation_name)
        else:
            iostream.stdout("Not ok")
            iostream.stderr("The path {} given doesn't exist".format(directory_or_file_path))

    def check_if_dock_already_exist(self, archive_name: str) -> bool:
        """
        Check if the documentation is already on the Confluence documentation repository.
        :param archive_name: The name of the archive.
        :return: A boolean.
        """
        iostream.stdout("Check if documentation is already on Confluence", StreamType.TITLE)
        response = requests.get(url=self.base_url + self.repository_url)
        data = response.json()
        for category in data["categories"]:
            for doc in category["docs"]:
                if doc["name"] == os.path.splitext(archive_name)[0]:
                    iostream.stdout("Already exist")
                    return True
        iostream.stdout("Don't exist")
        return False

    def get_directory_details(self):
        """
        Print the details of the Confluence documentation repository.
        """
        iostream.stdout("Get directory details", StreamType.TITLE)
        response = requests.get(url=self.base_url + self.repository_url)
        check_http_error(response)
        data = response.json()

        for category in data["categories"]:
            for doc in category["docs"]:
                iostream.stdout("Documentation id: {}  name: {}".format(doc["catId"] + "-" + doc["id"], doc["name"]))

    def check_documentation_id_validity(self, documentation_key: str) -> bool:
        """
        Check if the documentation id exist in Confluence repository.
        :param documentation_key: The unique key of the documentation in Confluence repository.
        :return: A boolean
        """
        iostream.stdout("Check document id validity", StreamType.TITLE)
        response = requests.get(url=self.base_url + self.repository_url)
        check_http_error(response)
        data = response.json()

        for category in data["categories"]:
            for doc in category["docs"]:
                if documentation_key == doc["catId"] + "-" + doc["id"]:
                    return True
        iostream.stdout("Not found")
        return False

    def check_documentation_category_id(self, category_key: str) -> bool:
        """
        Check if the category id in Confluence exist.
        :param category_key: The unique category id of a group of Documentation.
        :return: A boolean.
        """
        iostream.stdout("Check category id validity", StreamType.TITLE)
        response = requests.get(url=self.base_url + self.repository_url)
        check_http_error(response)
        data = response.json()

        for category in data["categories"]:
            if category_key == category["id"]:
                iostream.stdout("Ok")
                return True
        iostream.stdout("Not found")
        return False

    def create_documentation(self, category_key: str, archive_name: str, username: str, password: str):
        """
        Create a new documentation file in Confluence.
        :param category_key: The unique key of category.
        :param archive_name: The name of the archive.
        :param username: The username on Confluence.
        :param password: The password of Confluence user.
        :return: A boolean.
        """
        iostream.stdout("Create documentation on Confluence at {} with name {}".format(category_key, archive_name))
        if not self.check_documentation_category_id(category_key):
            iostream.stderr("Category key doesn't exist")

        try:
            h = {"X-Atlassian-Token": "nocheck",
                 "Authorization": "Basic {}".format(
                     base64.b64encode("{}:{}".format(username, password).replace("/n", "").encode()).decode()),
                 "Content-Type": "application/json"}
            documentation_name = os.path.splitext(os.path.split(archive_name)[1])[0]

            with open(archive_name, "rb") as file:
                response = requests.put(
                    self.base_url + self.repository_url + category_key + "/" + documentation_name,
                    headers=h,
                    verify=False,
                    auth=HTTPBasicAuth(username, password),
                    data=file)
                iostream.stdout(response.request.url)
                iostream.stdout(response.text)

            # If the response was successful, no Exception will be raised
            response.raise_for_status()

        except HTTPError as http_err:
            iostream.stdout("Not uploaded")
            iostream.stdout("Request send: " + response.request.url)
            iostream.stderr(f'HTTP error occurred: {http_err}')
        except Exception as err:
            iostream.stdout("Not uploaded")
            iostream.stdout(response.text)
            iostream.stderr(f'Other error occurred: {err}')
        else:
            iostream.stdout("Document uploaded successfully")

    def update_documentation(self, documentation_key: str, archive_name: str, username: str, password: str):
        """
        Update the documentation with the given key.
        :param documentation_key: The unique key of documentation file.
        :param archive_name: The name of the archive.
        :param username: The username on Confluence.
        :param password: The password of Confluence user.
        :return: A boolean.
        """
        if not self.check_documentation_id_validity(documentation_key):
            iostream.stderr("Key documentation doesn't exist")

        try:
            h = {"X-Atlassian-Token": "nocheck",
                 "Authorization": "Basic {}".format(
                     base64.b64encode("{}:{}".format(username, password).replace("/n", "").encode()).decode()),
                 "Content-Type": "application/json"}

            with open(archive_name, 'rb') as file:

                response = requests.post(self.base_url + self.repository_url + documentation_key,
                                         headers=h,
                                         verify=False,
                                         auth=HTTPBasicAuth(username, password),
                                         data=file)

                # If the response was successful, no Exception will be raised
                response.raise_for_status()
                iostream.stdout(response.request.url)
                iostream.stdout(response.text)

        except HTTPError as http_err:
            iostream.stdout("Not uploaded")
            iostream.stderr(f'HTTP error occurred: {http_err}')
        except Exception as err:
            iostream.stdout("Not uploaded")
            iostream.stderr(f'Other error occurred: {err}')
        else:
            iostream.stdout("Document uploaded successfully")

    def get_category(self, archive_name: str):
        iostream.stdout("Get category of {}".format(archive_name), StreamType.TITLE)
        response = requests.get(url=self.base_url + self.repository_url)
        data = response.json()
        for category in data["categories"]:
            for doc in category["docs"]:
                if doc["name"] == archive_name:
                    return doc["catId"]
        return ""

    def get_documentation_id(self, documentation_name: str) -> str:
        """
        Get the documentation id with the documentation name given.
        :param documentation_name: Documentation name.
        :return: The id of the documentation or an empty string.
        """
        iostream.stdout("Get id of {}".format(documentation_name), StreamType.TITLE)
        response = requests.get(url=self.base_url + self.repository_url)
        data = response.json()
        for category in data["categories"]:
            for doc in category["docs"]:
                if doc["name"] == documentation_name:
                    iostream.stdout("Id is {}".format(doc["catId"] + "-" + doc["id"]))
                    return doc["catId"] + "-" + doc["id"]
        iostream.stdout("")
        return ""

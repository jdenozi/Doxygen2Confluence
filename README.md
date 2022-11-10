# README

This script is used to do an automatic synchronisation of the documentation on the desired space in confluence.

## REQUIREMENT

- Python 3.XXX

## INSTALLATION

### Add to path

```
export PATH=$PATH:"{path}/syncDocToConfluence"

```

### Library installation

```pip install -r requirements.txt```

## USAGE

```
usage: syncToConfluence [-h] [-i INPUT] [-n NAME] [-u USER] [-p PASSWORD] [-di DOCUMENTATIONID] [-ci CATEGORYID] [-up] [-c CREATE] [-d] [-v] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Documentation html file
  -n NAME, --name NAME  Name of the documentation
  -u USER, --user USER  User name used for confluence connection
  -p PASSWORD, --password PASSWORD
                        Password used for confluence connection
  -di DOCUMENTATIONID, --documentationId DOCUMENTATIONID
                        Doc key of the document. Association of id and categories key.
  -ci CATEGORYID, --categoryId CATEGORYID
                        Doc key of the document. Association of id and categories key.
  -up, --update         Update document.
  -c CREATE, --create CREATE
                        Create new document.
  -d, --details         Get repository details.
  -v, --verbose         Add more details.
  -r, --remove          Remove documentation on Confluence repository.
```

### Example

```
python3 synDoc -u toto -p {mdp} -i ../../doc/html -up -ci c1007 -n TotoSoftware_v0.1.0
```
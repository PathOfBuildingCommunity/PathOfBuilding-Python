"""Functions for reading and writing xml."""

import pathlib

import xmltodict


def read_xml(file_name: pathlib.Path) -> dict | None:
    try:
        content = file_name.read_text()
    except FileNotFoundError:
        return
    return xmltodict.parse(content)


def write_xml(file_name: pathlib.Path, payload: dict):
    content = xmltodict.unparse(payload, pretty=True)
    try:
        pathlib.Path(file_name).write_text(content)
    except FileNotFoundError:
        print(f"Unable to write file {file_name}")

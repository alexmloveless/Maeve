import re
import json
import hjson
from os import path, walk


class FSUtils:

    @staticmethod
    def os_walk_and_filter(loc, dirregex: str = None, fileregex: str = None):
        """
        Recursively walk a file tree and filter based on args, returning a list of files
        Parameters
        ----------
        loc: str
            The location to start the search from
        dirregex: str
            Only directory names that match this regex will be traversed
        fileregex: str
            Only file names that match this regex will be traversed

        Returns
        -------
        A list of file names with their paths relative to the loc
        """
        files = []
        for i in walk(loc):
            if dirregex and not re.match(dirregex, i[0]):
                continue
            for j in i[2]:
                if fileregex and not re.match(fileregex, j):
                    continue
                files.append(path.join(i[0], j))
        return files

    @classmethod
    def read_conf_file(cls, filepath: str):
        """
        Reads a data file in various formats given a file location
        Will infer the file type from the file suffix
        Parameters
        ----------
        filepath: str
            Should be a fully qualified path

        Returns
        -------
        The contents for the file in dict form or None if it's not valid file path

        """
        if re.match(r".+\.json$", filepath):
            return cls.read_json_file(filepath)
        elif re.match(r".+\.hjson$", filepath):
            return cls.read_hjson_file(filepath)
        else:
            raise RuntimeError(f"Unknown file extension for file {filepath}")

    @staticmethod
    def read_json_file(f):
        """
        Reads a JSON file and returns in dict form
        Parameters
        ----------
        f: str
            Should be a fully qualified path
        Returns
        -------
        The contents for the file in dict form or None if it's not valid file path
        """
        try:
            with open(f, 'rb') as fh:
                return json.load(fh)
        except json.decoder.JSONDecodeError:
            raise RuntimeError(f"Invalid or malformed JSON in file {f}")

    @staticmethod
    def read_hjson_file(f):
        """
        Reads an HJSON file and returns in dict form
        Parameters
        ----------
        f: str
            Should be a fully qualified path
        Returns
        -------
        The contents for the file in dict form or None if it's not valid file path
        """
        try:
            with open(f, 'rb') as fh:
                return hjson.load(fh, object_pairs_hook=dict)
        except hjson.scanner.HjsonDecodeError:
            raise RuntimeError(f"Invalid or malformed HJSON in file {f}")


from maeve.util import Logger
from maeve.util import FSUtils, DictUtils, AnchorUtils
from maeve.models.core import ConfscadeDefaults, GlobalConst, EnvConf

from datetime import datetime
import json
from os import path, listdir
import logging
import re

from typing import Union, Optional


class Confscade:

    def __init__(self,
                 config,
                 env_conf: dict = None,
                 defaultkey: str =None,
                 global_default_conf: dict = None,
                 error_on_notfound: bool = None,
                 recursive_dir: bool = None,
                 log_level: str = None,
                 log_location: str = None,
                 logger=None
                 ):
        """
        Read and parse JSON config file

        Parameters
        ----------
        config: str, list
            A path to a valid Marty (H)JSON config file.
            A path to a directory (or directory tree) that contains valid Marty config files.
            A list containing any mixture of the above.
        defaultkey: str
            The name of the default key in this file. Default is "default"
        error_on_notfound: bool
            Whether to raise an error when a file is not found. If False an no file is found, a JSONConf instance
            is returned with an empty conf dict. Conf items can then be added after the fact.
        log_level: str
            The log level,
        logger: object
            A logger instance - either a python or maeve logger instance should work
        """
        if env_conf:
            self.e = env_conf
        else:
            self.e = EnvConf()

        if logger:
            self.log = logger
        else:
            self.log = Logger(log_level=log_level, log_maxlen=self.e.log_maxlen, log_location=log_location)

        self.g = GlobalConst()

        self.fs = FSUtils()

        confdict = self.filter_args({
            "GLOBAL_DEFAULT_CONF": global_default_conf,
            "RECURSIVE_FLAG": recursive_dir,
            "ERROR_ON_NOTFOUND": error_on_notfound,
            "DEFAULT_CONF_KEY": defaultkey
        })

        self.d = ConfscadeDefaults(**confdict)

        self.conf = {}
        self.get_conf(config)

    @staticmethod
    def filter_args(d: dict) -> dict:
        return {k: v for k, v in d.items() if v is not None}

    def get(self,
            name: str,
            inherits: dict = None,
            exceptonmissing: bool = False,
            parse_anchors: bool = True,
            anchors: dict = None
            ) -> dict:
        """
        Given a valid conf name returns a fully resolved config

        Parameters
        ----------
        name: str
            The name of conf item
        inherits: dict
            A valid conf item in dict form. The requested conf item will be merged on top of this
        exceptonmissing: bool
            If True and excpetion is thrown if the requested item is missing, otherwise will fall be on defualts
            (probably an empty dict)

        Returns
        -------
        The requested item in dictionary form

        """
        d = self.confscade(self.conf, name, inherits=inherits, exceptonmissing=exceptonmissing)
        if parse_anchors:
            return AnchorUtils.resolve_anchors(self.conf, d, anchors=anchors, env_conf=self.e)
        else:
            return d

    def items(self):
        return list(self.conf.keys())

    def get_conf(self, config: Optional[Union[list, dict, str]] = None):
        if config:
            type_config = type(config)
            if type_config is str:
                try:
                    self.conf = json.loads(config)
                except (ValueError, TypeError):
                    self.get_conf_from_files(config)

            elif type_config in [dict, list]:
                if type_config is dict:
                    config = list(config.values())
                self.get_conf_from_files(config)
            else:
                self.log.warning("Invalid data type, using global_default_conf")
                self.conf = {}

        else:
            self.log.warning("No config info provided, using global_default_conf")
            self.conf = {}

        # We add in a global default so that there's always something for cascading confs to roll up to
        if not self.conf:
            self.log.warning("No valid JSON config files found, using global_default_conf")
        self.conf = DictUtils.mergedicts(self.d.GLOBAL_DEFAULT_CONF, self.conf)

    def get_conf_from_files(
            self,
            filepath: Union[str, list],
            fileregex: str = r".+\.h?json$",
    ):

        if type(filepath) is not list:
            filepath = [filepath]

        for i in filepath:
            if path.exists(i):
                if path.isdir(i):
                    self.log.debug("Found JSON conf directory, searching for valid files")
                    if self.d.RECURSIVE_FLAG:
                        for j in self.fs.os_walk_and_filter(i, fileregex=fileregex):
                            self.load_and_merge(j)
                    else:
                        for j in listdir(i):
                            if re.match(fileregex, j):
                                self.load_and_merge(j)
                else:
                    if re.match(fileregex, i):
                        self.load_and_merge(i)
                    else:
                        self.log.debug("Skipping file as it file extension not recognised {}".format(i))
            else:
                self.log.warning(f"Config location {i} doesn't exist, ignoring")

    def load_and_merge(self, filepath: str):
        c = self.fs.read_conf_file(filepath)
        if not c:
            return
        self.log.debug("Merging config file: {}".format(filepath))
        c = self.analyse_conf(c, filepath)
        if c:
            self.conf = DictUtils.mergedicts(self.conf, c)
        else:
            self.log.debug("No valid conf found in file {}. Check if ignore=True in default section.".format(filepath))

    def analyse_conf(self, c, f):

        default = c.get(self.d.DEFAULT_CONF_KEY, {})

        if not default:
            self.log.debug("No default key or empty dict found in file {}".format(f))
        else:
            # The whole file is ignored if ignore=True is set int he default section
            if default.get("ignore", False):
                return {}

        if self.d.DEFAULT_CONF_KEY in c.keys():
            del c[self.d.DEFAULT_CONF_KEY]

        for k, v in c.items():

            if k in self.conf.keys():
                self.log.warning(
                    "Key {} from {} already seen. Will attempt to merge but results may be unpredictable.".format(k, f)
                )

            if v.get("ignore", False):
                del c[k]
                continue

            # merge up to the local (file) default
            v = DictUtils.mergedicts(default, v)
            if "metadata" not in v.keys():
                v["metadata"] = {}
            v["metadata"]["conf_file"] = f
            v["metadata"]["loaded"] = self.str_date_time_now()

            # backward compatibility
            if "description" in v.keys():
                v["metadata"]["short_description"] = v["description"]
                del v["description"]
            if "data_dictionary" in v.keys():
                v["metadata"]["data_dictionary"] = v["data_dictionary"]
                del v["data_dictionary"]
            c[k] = v
        return c

    def add_conf(self, name, cfg):
        self.conf[name] = cfg

    def find_key(self, key, name=None):
        if not name:
            return DictUtils.search_dict(self.conf, key)
        else:
            return DictUtils.search_dict(self.confscade(self.conf, name), key)


    def pretty_print(self, item):
        return json.dumps(item, indent=4)


    def pretty_print_conf(self, name):
        c = self.confscade(self.conf, name)
        return self.pretty_print(c)

    def str_date_time_now(self):
        return datetime.now().strftime(self.d.OUTPUT_DATETIME_FMT)

    def load_json_string(self, j):
        try:
            return json.loads(j)
        except (ValueError, TypeError):
            # cls.log.degug("String passed not valid JSON")
            return j

    def confscade(self, conf, key, inherits=None, exceptonmissing=False):
        """
        Gets JSON conf by `key` using the default template to fill in any
        blanks. If `key` not found returns default

        Parameters
        ----------
        conf : dict
            The config file
        key : str
            The key for the conf required

        Returns
        -------
        dict
            a conf dict

        """
        try:
            c = conf[key]
        except KeyError:
            if exceptonmissing:
                raise KeyError("Unknown config item: {}".format(key))
            else:
                return self.confscade(conf, self.d.DEFAULT_CONF_KEY)

        if not inherits:
            if "inherits" in c.keys():
                default = self.confscade(conf, c['inherits'])
            else:
                default = DictUtils.mergedicts(
                    self.d.GLOBAL_DEFAULT_CONF[self.d.DEFAULT_CONF_KEY],
                    conf.get(self.d.DEFAULT_CONF_KEY, self.d.MINIMUM_CONF)
                )
        else:
            default = inherits

        return DictUtils.mergedicts(default, c)

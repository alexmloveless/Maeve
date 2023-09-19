


import logging
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s:%(message)s')

class Globals:

    packagename = "maeve"
    datapackagestub = "mv"

    var_conf_value_field = "value"

    # anchors
    anchor_prefix = "@"
    anchor_match_regex = r"^@[\w+]"
    anchor_sub_regex = r"^@"
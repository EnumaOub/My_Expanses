# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 19:14:19 2023

@author: rayan
"""

from configparser import ConfigParser

def set_config(filename="D:\Learn\Python\First_Flask\First_Flask\sql\config.ini", section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
# -*- coding: utf-8 -*-
#
# Copyright 2018-2021 Bartosz Kryza <bkryza@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility functions."""

import inspect
import logging as LOG
import re

import six


def render_path(path, args):
    """Render REST path from *args."""
    LOG.debug('RENDERING PATH FROM: %s,  %s', path, args)
    result = path
    matches = re.search(r'{([^}.]*)}', result)
    while matches:
        path_token = matches.group(1)
        if path_token not in args:
            raise ValueError("Missing argument %s in REST call" % (path_token))
        result = re.sub('{%s}' % (path_token), str(args[path_token]), result)
        matches = re.search(r'{([^}.]*)}', result)
    return result


def dict_from_args(func, *args):
    """Convert function arguments to a dictionary."""
    result = {}
    args_names = []
    args_default_values = ()

    if six.PY2:
        args_names = inspect.getargspec(func)[0]
        args_default_values = inspect.getargspec(func)[3]
        # Add bound arguments to the dictionary
        for i in range(len(args)):
            result[args_names[i]] = args[i]

        # Add any default arguments if were left unbound in method call
        for j in range(len(args), len(args_names)):
            result[args_names[j]] = args_default_values[len(args_names) -
                                                        (j + len(args) - 1)]
    else:
        parameters = inspect.signature(func).parameters
        idx = 0
        for name, parameter in parameters.items():
            if idx < len(args):
                # Add bound arguments to the dictionary
                result[name] = args[idx]
                idx += 1
            elif parameter.default is not inspect.Parameter.empty:
                # Add any default arguments if were left unbound in method call
                result[name] = parameter.default
                idx += 1
            else:
                pass

    return result


def merge_dicts(*dict_args):
    """
    Merge all dicts passed as arguments, skips None objects.

    Repeating keys will replace the keys from previous dicts.
    """
    result = None
    for dictionary in dict_args:
        if dictionary is not None:
            if result is None:
                result = dictionary
            else:
                result.update(dictionary)
    if result is None:
        result = {}
    return result


def normalize_url(url):
    """Make sure the url is in correct form."""
    result = url

    if not result.endswith("/"):
        result = result + "/"

    return result

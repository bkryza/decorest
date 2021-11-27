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
"""Defines various error classes."""


class HTTPErrorWrapper(Exception):
    """
    Wrap an HTTP error from different backends.

    This error class wraps HTTP errors from different supported
    backends, i.e. requests and httpx.
    """
    def __init__(self, e):
        """Construct HTTPErrorWrapper.

        Accepts a wrapped error.
        """
        self.wrapped = e
        super(Exception, self).__init__(self)

    @property
    def response(self):
        """Return wrapped response."""
        return self.wrapped.response

    def __repr__(self):
        """Return wrapped representation."""
        return self.wrapped.__repr__()

    def __str__(self):
        """Return wrapped str representation."""
        return self.wrapped.__str__()

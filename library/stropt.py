#!/usr/bin/env python
# -*- coding:utf-8 -*-


import hashlib


def get_md5(src):

    new = hashlib.md5()
    new.update(src)
    return new.hexdigest()

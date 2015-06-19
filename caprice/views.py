#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for

from .models import *

api = Blueprint('api', __name__)

@api.route('/schemas')
def schema():
    return ''

@api.route('/resources')
def resource():
    return ''

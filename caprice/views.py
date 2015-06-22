#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, Response
from flask import render_template, redirect, url_for, request

from .models import *

api = Blueprint('api', __name__)

@api.route('/schemas', methods=['GET', 'POST'])
def schema():
    res = Response('')
    if request.method == 'POST':
        res.status_code = 201
    return res

@api.route('/schemas/<int:_id>', methods=['GET', 'DELETE'])
def schema_id(_id):
    res = Response('')
    res.data = str(_id)
    if request.method == 'DELETE':
        res.status_code = 204
    return res

@api.route('/resources', methods=['GET', 'POST'])
def resource():
    res = Response('')
    if request.method == 'POST':
        res.status_code = 201
    return res

@api.route('/resources/<int:_id>', methods=['GET', 'PUT', 'DELETE'])
def resource_id(_id):
    res = Response('')
    res.data = str(_id)
    if request.method == 'DELETE':
        res.status_code = 204
    return res

@api.route('/locks', methods=['GET', 'POST'])
def lock():
    res = Response('')
    if request.method == 'POST':
        res.status_code = 201
    return res

@api.route('/locks/<int:_id>', methods=['GET', 'DELETE'])
def lock_id(_id):
    res = Response('')
    res.data = str(_id)
    if request.method == 'DELETE':
        res.status_code = 204
    return res

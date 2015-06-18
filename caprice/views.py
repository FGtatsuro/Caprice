#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for

from .models import *

main = Blueprint('main', __name__)

@main.route('/')
def root():
    return redirect(url_for('.index'))

@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/items')
def items():
    items = Dummy()
    return render_template('items.html', items=items)

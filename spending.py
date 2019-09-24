import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from finTrack.db import get_db

bp = Blueprint('spending', __name__, url_prefix='/spending')
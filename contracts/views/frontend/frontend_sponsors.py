###########################################################################################
# frontend_sponsorship - frontend sponsorship views
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/08/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################
'''
frontend_sponsorship - frontend sponsorship views
=======================================================================

Supports sponsorship views for frontend
'''
# standard
from operator import itemgetter
from json import dumps, loads
from collections import OrderedDict
from traceback import format_exc
from datetime import datetime

# pypi
from flask import current_app, request, jsonify, render_template, url_for
from flask.views import MethodView

# home grown
from . import bp
from contracts.dbmodel import db, SponsorRace, SponsorLevel, SponsorBenefit, SponsorQueryLog
from contracts.mailer import sendmail
from loutilities.flask_helpers.blueprints import add_url_rules
from loutilities.timeu import asctime
dt = asctime('%Y-%m-%d %H:%M:%S')

class parameterError(Exception): pass

#######################################################################
class SponsorshipQuery(MethodView):
#######################################################################
    url_rules = {
                'sponsorship-query': ['/sponsorshipquery',('GET','POST',)],
                }

    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        
        # build levels by race
        levelsdata = SponsorLevel.query.all()
        levels = OrderedDict()
        for level in levelsdata:
            thislevel = {
                'levelname': level.level,
                'minsponsorship': level.minsponsorship,
                # TODO: determine display based on level.maxallowed and current sponsors configuration
                'display': level.display,
            }
            levels.setdefault(level.race.race, []).append(thislevel)

        # sort levels for each race high to low, i.e., most important first, supports form display
        for thisrace in levels:
            levels[thisrace] = sorted(levels[thisrace], key=itemgetter('minsponsorship'), reverse=True)

        # get races, build structure
        racesdata = SponsorRace.query.all()
        races = OrderedDict()
        for race in racesdata:
            races[race.race] = {k:v for k,v in race.__dict__.items() if k[0:4] != "_sa_"}

        context = {
                   'pagename'         : 'request sponsorship',
                   'pageassets_css'   : 'page-sponsorship-query-css',
                   'pageassets_js'    : 'page-sponsorship-query-js',
                   'sponsorshipquery_contact' : current_app.config['SPONSORSHIPQUERY_CONTACT'],
                   'races'            : races,
                   'races_json'       : dumps(races, sort_keys=True),
                   'levels'           : levels,
                   'levels_json'      : dumps(levels, sort_keys=True),
                  }
        return render_template( 'sponsorship-form.jinja2', **context )

    #----------------------------------------------------------------------
    def post(self):
    #----------------------------------------------------------------------
        try:
            # request.form is werkzeug.datastructures.ImmutableMultiDict
            # and each field will show up as list if we don't convert to dict here
            # form = {k:v for k,v in request.form.items()}
            form = loads(request.form['json'])

            # figure out RD for this race
            race = SponsorRace.query.filter_by(race=form['race']['text']).one()
            rdemail = race.email


            # log this request, won't be committed until after sendmail
            log = SponsorQueryLog(**{k:form[k]['text'] for k in form['_keyorder']})
            log.time = dt.dt2asc(datetime.now())
            db.session.add(log)

            # turn form into email
            html = render_template( 'sponsorship-email.jinja2', formdata=form)

            subject = 'Thanks for sponsoring {}!'.format(race.race)

            # TODO: these could be in database
            tolist = '{} <{}>'.format(form['name']['text'], form['email']['text'])
            cclist = [rdemail] + current_app.config['SPONSORSHIPQUERY_CC']
            fromlist = '{} <{}>'.format(race.race, current_app.config['SPONSORSHIPQUERY_CONTACT'])
            sendmail( subject, fromlist, tolist, html, ccaddr=cclist )

            # everything seemed to work ok, so committing
            db.session.commit()

            return 'OK'

        except:
            return "<br/>{}".format(format_exc())

#----------------------------------------------------------------------
add_url_rules(bp, SponsorshipQuery)
#----------------------------------------------------------------------
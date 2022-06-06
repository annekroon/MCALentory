from flask import Flask, render_template, url_for, redirect, abort
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import json
from wtforms import validators, Form
import os

app = Flask(__name__)
app.config['demo'] = os.environ.get('IS_DEMO', True)
app.config['is_production'] = os.environ.get('IS_PRODUCTION', False)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '0012345679')
app.config['GA_TRACKING_ID'] = os.environ.get('GA_TRACKING_ID', None)

# set bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = os.environ.get('FLASK_ADMIN_SWATCH', 'lumen')#'lumen' 'paper'

# db config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres://anne@localhost:5432/template1')
app.config['SQLALCHEMY_ECHO'] = not (app.config['is_production'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])


# customs views
class ModelViewProduct(ModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    export_types = ['csv', 'xls']
    column_labels = dict(author='Authors',
                         journal='Journal',
                         doi = 'Doi',
                         scope = 'Content',
                         concept = 'Key concept',
                         start_year = 'Start research period',
                         end_year = 'End research period',
                         RQ = 'Type of RQ',
                         url = 'URL',
                         openaccess = 'Open acces',
                         comparative = 'Comparative analysis' ,
                         preregistered = 'Preregistered',
                         reliability_measure = 'Measure for reliability',
                         urltosource = 'URL to data'
                         )

    column_filters = ['id', 'author', 'journal','doi', 'scope', 'start_year','end_year', 'RQ', 'url', 'openaccess', 'comparative', 'preregistered',
                      'time_created', 'time_updated', 'reliability_measure','urltosource',]

    page_size = 20

    column_exclude_list = ['time_created', 'time_updated', 'available', 'url']
    column_searchable_list = ['author', 'journal', 'scope', 'RQ', 'start_year','end_year', 'reliability_measure']
    column_editable_list = ['urltosource', ]
    form_excluded_columns = ['time_created', 'time_updated']


    form_args = {
        'author': {
            'label': 'Study Name'
        },
        'journal': {
            'label': 'Study Description'
        }
    }
    form_widget_args = {
        'journal': {
            'rows': 10,
            'style': 'color: black'
        }
    }


# customs views
class ModelViewTools(ModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    export_types = ['csv', 'xls']

    column_filters = ['id',
                      'time_created', 'time_updated']
    page_size = 20

    column_exclude_list = ['time_created', 'time_updated']
    column_searchable_list = []
    column_editable_list = []
    form_excluded_columns = ['time_created', 'time_updated']


class Studies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), unique=True, nullable=False)
    journal = db.Column(db.TEXT)
    doi = db.Column(db.String(100),unique=True, nullable=False)
    scope = db.Column(db.TEXT)
    concept = db.Column(db.TEXT)
    RQ = db.Column(db.TEXT)
    url = db.Column(db.TEXT)
    comparative = db.Column(db.TEXT)
    available = db.Column(db.TEXT)
    preregistered= db.Column(db.TEXT)
    openaccess = db.Column(db.TEXT)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    reliability_measure = db.Column(db.TEXT)
    urltosource = db.Column(db.TEXT)
    time_created = db.Column(db.TIMESTAMP, server_default=db.func.now())
    time_updated = db.Column(db.TIMESTAMP, onupdate=db.func.now(), server_default=db.func.now())

    def __str__(self):
        return "{}".format(self.author)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #author = db.Column(db.String(100), unique=True, nullable=False)
    #other_details = db.Column(db.TEXT)
    time_created = db.Column(db.TIMESTAMP, server_default=db.func.now())
    time_updated = db.Column(
        db.TIMESTAMP, onupdate=db.func.now(), server_default=db.func.now())

    def __str__(self):
        return "{}".format(self.author)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())


admin = Admin(app, name='Inventory Management',
              template_mode='bootstrap3', url='/', base_template='admin/custombase.html')

admin.add_view(ModelViewProduct(Studies, db.session, name='Studies', category="Inventory of MCA Studies"))
#admin.add_view(ModelViewLocation(Location, db.session, category="Inventory of MCA Studies"))
admin.add_view(ModelViewTools(Location, db.session, name="Inventory of Tools and Data"))


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

# init demo data
def create_demo_data():

    with open("MCAL_inventory.json", "r") as fi:
        inventory_data = [json.loads(line) for line in fi]



    for entry in inventory_data:
        print(entry)
        studies = Studies()
        studies.author = entry['Authors']
        studies.journal = entry['Journal']
        studies.doi = entry['clean_doi']
        studies.scope = entry['Type of material? (Newspaper coverage, Television coverage, Online content, Social media content, Other: namely…)']
        studies.concept = entry['Which media variables were coded? (Issue attention, Actor visibility, Sentiment, Issue-specific frames, Generic frames, Other: namely …)']
        studies.period = entry['Period (in years)']
        studies.RQ = entry['Type of RQ? (descriptive, explaining media content, effects on citizens, effects on policy/politics, other namely:...)']
        studies.url =entry['Link']
        studies.comparative = entry['comparative']
        studies.available = entry['Data available? (Yes = 1)']
        studies.preregistered = entry['Is the study pre-registered? ']
        studies.openaccess = entry['Is the publication open access? (author version and gold open access) (Yes = 1)']
        studies.start_year = entry['start_year']
        studies.end_year = entry['end_year']
        studies.reliability_measure = entry['If yes, which one? (Pairwise/percentage agreement?, Krippendorff’s alpha, Cohen’s kappa, Lotus, Precision, Recall, Other: namely)']
        studies.urltosource=entry['Link to data/syntax/…']
        db.session.add(studies)

    db.session.commit()
    return


if __name__ == "__main__":
    # create demo data if demo flag set
    if app.config['demo']:
        #db.metadata.drop_all()
        db.drop_all()
        db.create_all()
        create_demo_data()
    debug = not (app.config['is_production'])
    app.run(debug=debug)

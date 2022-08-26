from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from utils import *

from flask import Flask, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

server = Flask(__name__)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], server=server, url_base_pathname='/dash/')
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("123"),
    "spandan": generate_password_hash("patil")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@server.route('/')
@auth.login_required
def index():
    return redirect('/dash/')

app.layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            html.A(dbc.Row([
                dbc.Col(dbc.NavbarBrand("Jobs Dashboard by Spandan", className="ms-2")),
            ],
                align="center",
                className="g-0",
            ),
                href="/",
                style={"textDecoration": "none"},
            )
        ]),
        color="dark",
        dark=True,
    ),

    dbc.Container([
        html.Div([
            dbc.Card([
                dbc.CardBody([
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([dbc.Col(html.H4('Select State (or search in the box)'),width='auto'),
                                         dbc.Col([html.I(className="bi bi-info-circle-fill",id='popover-warning'),
                                                  dbc.Popover(
                                                      dbc.PopoverBody("All States will give results for all the states. Others will give result for that specific state only"),
                                                      target='popover-warning',
                                                      trigger='hover',

                                                  )])]),
                                dbc.Row([dcc.Dropdown(['All States']+states_list, 'All States', id='state-dropdown', clearable=False)])
                            ], width=6),
                        ], justify='center'),

                        html.Hr(),

                        dbc.Row([
                            dbc.Col([
                                dbc.Row([html.H4('Select Category (or search in the box)')]),
                                dbc.Row([dcc.Dropdown(categories, 'Aerospace & Aviation', id='categories-dropdown', clearable=False)])
                            ]),

                            dbc.Col([
                                dbc.Row([dbc.Col(html.H4('Select Sub-category (or search in the box)'),width='auto'),
                                         dbc.Col([html.I(className="bi bi-info-circle-fill",id='popover-warning-subcategory'),
                                                  dbc.Popover(
                                                      dbc.PopoverBody("Some sub-categories will be disabled as no jobs are found in DB for them"),
                                                      target='popover-warning-subcategory',
                                                      trigger='hover',

                                                  )])]),
                                dbc.Row([dcc.Dropdown([], 'Aerospace Materials Specialist', id='subcategories-dropdown', clearable=False)])
                            ]),
                        ]),


                    ])
                ])
            ]),

            html.Br(),
            dbc.Card([
                dbc.CardHeader([html.H4('Job Listings', style={'textAlign': 'center'}, id='job-listings-title')]),
                dbc.CardBody(
                    dbc.Container([], style={'height': '500px', 'overflowY': 'scroll'}, id='job-listings')
                )
            ], style={'width':'75%', 'margin':'auto'})

        ])
    ])
])

@app.callback(Output('subcategories-dropdown', 'options'),
                [Input('categories-dropdown', 'value'),
                 Input('state-dropdown', 'value')])
def update_subcategories(category, state):
    subcategoryList = conn.execute("SELECT SUBCATEGORY FROM SUBCATEGORIES WHERE CATEGORY = ?", (category,)).fetchall()
    subcategoryList = sorted([i[0] for i in subcategoryList])

    if(state == 'All States'):
        subcategoryList2 = conn.execute("""SELECT DISTINCT(JOBS.SUBCATEGORY)
        FROM SUBCATEGORIES
        LEFT JOIN JOBS
        ON SUBCATEGORIES.SUBCATEGORY = JOBS.SUBCATEGORY
        WHERE JOBS.SUBCATEGORY IS NOT NULL AND SUBCATEGORIES.CATEGORY = ?""",
                                        (category,)).fetchall()
    else:
        subcategoryList2 = conn.execute("""SELECT DISTINCT(JOBS.SUBCATEGORY)
        FROM SUBCATEGORIES
        LEFT JOIN JOBS
        ON SUBCATEGORIES.SUBCATEGORY = JOBS.SUBCATEGORY
        WHERE JOBS.SUBCATEGORY IS NOT NULL AND SUBCATEGORIES.CATEGORY = ? AND JOBS.LOCATION_STATE=?""",
                                        (category, state)).fetchall()

    subcategoryList2 = sorted([i[0] for i in subcategoryList2])
    newList=[]
    for i in subcategoryList:
        if i in subcategoryList2:
            newList.append({'label': i, 'value': i})
        else:
            newList.append({'label': i, 'value': i, 'disabled': True})

    return newList




@app.callback([Output('job-listings', 'children'),
               Output('job-listings-title', 'children')],
                [Input('state-dropdown', 'value'),
                Input('subcategories-dropdown', 'value')])
def joblistcontainer(state, subcategory):
    if state == 'All States':
        jobListings = conn.execute("SELECT * FROM JOBS WHERE SUBCATEGORY = ?", (subcategory,)).fetchall()
    else:
        jobListings = conn.execute("SELECT * FROM JOBS WHERE LOCATION LIKE ? AND SUBCATEGORY = ?", ('%{}'.format(state), subcategory)).fetchall()
    resList = []
    index=1
    for i in jobListings:
        df = pd.DataFrame(
            {
                'Sr. No.':['Job Name', 'Company', 'Location'],
                str(index):[i[2], i[1], i[3]]
            }
        )
        resList.append(
            dbc.Table.from_dataframe(df, striped=True, hover=True, borderless=True, style={'width':'50%', 'margin':'auto', 'border-style':'solid'})
        )
        index+=1

    br_index=1
    for i in range(len(resList)-1):
        resList.insert(i+br_index, html.Br())
        br_index+=1
    return resList, 'Job Listings ({} records found)'.format(len(jobListings))






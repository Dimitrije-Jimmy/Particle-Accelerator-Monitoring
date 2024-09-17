import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import threading
from sqlalchemy import create_engine
from typing import Optional, Dict, Tuple

# Import the sensor class
from device_app.sensor1 import TemperatureSensor
from device_app.sensor2 import PressureSensor
from device_app.sensor3 import RadiationSensor

from device_app.monitoring_service import MonitoringService

from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access environment variables
#db_name = os.getenv("DB_NAME")
#db_user = os.getenv("DB_USER")
#db_password = os.getenv("DB_PASSWORD")
#db_host = os.getenv("DB_HOST")
#db_port = os.getenv("DB_PORT")
database_url = os.getenv("DATABASE_URL")

# Database connection string
#db_engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
db_engine = create_engine(database_url)

# Initialize the Dash app
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Initialize the TemperatureSensor
temperature_sensor = TemperatureSensor(name="temperature_sensor", db_conn=db_engine.raw_connection())
# Initialize the PressureSensor
pressure_sensor = PressureSensor(name="pressure_sensor", db_conn=db_engine.raw_connection(), loglogs=True)
# Initialize the RadiationSensor
radiation_sensor = RadiationSensor(name="radiation_sensor", db_conn=db_engine.raw_connection())

sensor_details = {
    'temperature_sensor': {
        'sensor': temperature_sensor,
        'data_column': 'temperature',
        'xaxis_title': 'Temperature (°C)'
    },
    'pressure_sensor': {
        'sensor': pressure_sensor,
        'data_column': 'pressure',
        'xaxis_title': 'Pressure (bar)'
    },
    'radiation_sensor': {
        'sensor': radiation_sensor,
        'data_column': 'radiation',
        'xaxis_title': 'Radiation (mSv/h)'
    }
}

# Import experiment modules
import threading
import experiment_app.experiment1 as experiment1
import experiment_app.experiment2 as experiment2
import experiment_app.experiment3 as experiment3
from queue import Empty  # Import Empty exception for queues

# Function to get the log message from the queue
def get_log_message(log_queue):
    try:
        # Try to get the message from the queue with a timeout
        return log_queue.get(timeout=2)
    except Empty:
        return "No log message returned."


# Functions ------------------------------------------------------------------------------------

def build_banner() -> html.Div:
    """
    Builds the banner component for the application.

    Returns:
        html.Div: The banner component containing the application title, logo, and learn more button.
    """
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Particle Accelerator Monitoring"),
                    html.H6("Process Control and Exception Reporting"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button",
                        children="LEARN MORE",
                        n_clicks=0,
                    ),
                    # TO DO: add my photo and link to github for funs :)
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("Cosylab-logo-2023.png")),
                        href="https://plotly.com/dash/",
                    ),
                ],
            ),
        ],
    )


def build_tabs() -> html.Div:
    """
    Builds the tab component for the application.

    Returns:
        html.Div: The tab component containing the application's tabs.
    """
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab1",   # Set the default tab
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Control Charts Dashboard",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Specs-tab",
                        label="Specification Settings",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Experiments-tab",
                        label="Control Experiments",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    )
                ],
            )
        ],
    )



def generate_modal() -> html.Div:
    """
    Generates a modal component for the application.

    The modal includes a markdown container with a close button and a markdown text area.
    The markdown text area displays a description of the application, its features, and usage instructions.

    Returns:
        html.Div: The modal component.
    """
    return html.Div(
        id="markdown",
        className="modal",
        n_clicks=0,  # Make the modal background clickable
        children=html.Div(
            id="markdown-container",
            className="markdown-container",
            children=[
                html.Div(
                    className="close-container",
                    children=html.Button(
                        "Close",
                        #"X",
                        id="markdown_close",
                        n_clicks=0,
                        className="closeButton",
                    ),
                ),
                html.Div(
                    className="markdown-text",
                    children=dcc.Markdown(
                       
                        """
                        ###### What is this mock app about?

                        This dashboard is designed for real-time monitoring of sensor data and process quality in a manufacturing environment. It simulates a production line where multiple sensors collect data, allowing operators to visualize and control the manufacturing process efficiently.

                        ###### What does this app show?

                        - **Live Sensor Data**: Displays real-time measurements from various sensors such as temperature and pressure sensors.

                        - **Control Charts**: Visualizes sensor data over time with upper and lower control limits to monitor process stability.

                        - **Histograms**: Shows the distribution of sensor measurements alongside the control charts for a comprehensive view of data variability.

                        - **Sensor Logs**: Provides a detailed log of sensor activities, alerts, and status updates for troubleshooting and record-keeping.

                        ###### How to use the app

                        - **Select Device**: Use the dropdown menu in the dashboard to switch between different sensors (e.g., Temperature Sensor, Pressure Sensor). The dashboard will update to display data and controls specific to the selected sensor.

                        - **Sensor Controls**: Start or stop the sensor and initiate or halt measurements using the control buttons. The sensor's status is displayed with color-coded text indicating whether it's running, idle, or measuring.

                        - **Time Interval Selection**: Choose the desired time interval for data visualization (e.g., last 5 minutes, last hour, last day) from the dropdown menu to filter the displayed data accordingly.

                        - **Interact with Charts**: Click on data points within the control chart to see specific measurement details. The histogram beside the chart provides insight into the data distribution within the selected time frame.

                        - **View Logs**: Scroll through the sensor logs to monitor real-time alerts, errors, or status changes. This helps in quickly identifying and addressing any issues that may arise during operation.

                        ###### Features

                        * **Real-Time Monitoring**: The dashboard updates every few seconds, providing up-to-date information on sensor readings and process conditions.

                        * **Process Control Visualization**: Control charts help detect out-of-control conditions, enabling proactive adjustments to the manufacturing process.

                        * **Multiple Sensor Support**: Seamlessly switch between different sensors to monitor various aspects of the production line.

                        * **Interactive Controls**: Intuitive buttons and dropdowns make it easy to control sensor operations and customize data views.

                        * **Alerts and Logging**: Immediate alerts for out-of-control measurements and a comprehensive log system for tracking sensor activities.

                        ---

                        ###### Source Code

                        You can find the source code of this app on my [GitHub repository](https://github.com/Dimitrije-Jimmy/Particle-Accelerator-Monitoring). Feel free to explore, contribute, or customize it to suit your specific needs.

                        ---

                        This dashboard serves as a mock application demonstrating how real-time data visualization and process control can be implemented in a manufacturing setting. It provides a foundation that can be expanded upon for more complex systems and integrated with actual sensor hardware.
                        """
                    ),
                ),
            ],
        ),
    )


# Layout of the Dash app -------------------------------------------------------------------------

app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        
        # Stores for experiment states
        dcc.Store(id='experiment1-state', data={'running': False, 'bias': False, 'failure': False}),
        dcc.Store(id='experiment2-state', data={'running': False, 'bias': False, 'failure': False}),
        dcc.Store(id='experiment3-state', data={'running': False, 'bias': False, 'failure': False}),

        # Main app container
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app content
                html.Div(id="app-content"),
            ],
        ),
        generate_modal(),
    ],
)


def build_tab1() -> html.Div:
    """
    Builds the content for the first tab of a dashboard.

    Returns:
        A dash.html.Div object containing the tab's content.
    """
    return html.Div([
        #html.H3('Sensor Dashboard'),
        html.Hr(),
        dbc.Row([
            # Left Column: Device Selection and Controls
            dbc.Col([
                html.H3('Sensor Dashboard', style={'padding-left': '50px'}),
                #html.H3('Sensor Dashboard', style={'max-width': 'fit-content', 'margin-left': 'auto', 'margin-right': 'auto'}),
                html.Hr(),
                html.H4('Select Device', style={'padding-left': '10px'}),
                dcc.Dropdown(
                    id='device-selector',
                    options=[
                        {'label': 'Temperature Sensor', 'value': 'temperature_sensor'},
                        {'label': 'Pressure Sensor', 'value': 'pressure_sensor'},
                        {'label': 'Radiation Sensor', 'value': 'radiation_sensor'},
                    ],
                    value='temperature_sensor',
                    style={'width': '80%',
                           'padding-left': '10px'}
                ),
                html.Hr(),
                # This seems to look better thnnx Aleksandra
                html.Div([
                    html.H4('Select Time Interval', style={'padding-left': '10px'}),
                    dcc.Dropdown(
                        id='time-interval',
                        options=[
                            {'label': 'Last 5 Minutes', 'value': '5min'},
                            {'label': 'Last 15 Minutes', 'value': '15min'},
                            {'label': 'Last Hour', 'value': '1h'},
                            {'label': 'Last 12 Hours', 'value': '12h'},
                            {'label': 'Last Day', 'value': '1d'},
                            {'label': 'Last 5 Days', 'value': '5d'},
                            {'label': 'Last Month', 'value': '1M'},
                        ],
                        value='1h',
                        #style={'width': '50%'}
                        style={'width': '80%',
                               'padding-left': '10px'}
                    ),
                ], style={'margin-bottom': '20px'}),

                html.Hr(),
                html.Div([
                    html.H4('Sensor Controls', style={'padding-left': '10px'}),
                    html.Button('Start Sensor', id='start-sensor', n_clicks=0, style={'margin-left': '10px'}),
                    html.Button('Stop Sensor', id='stop-sensor', n_clicks=0, style={'margin-left': '10px'}),
                    html.Button('Start Measuring', id='start-measuring', n_clicks=0, style={'margin-left': '10px'}),
                    html.Button('Stop Measuring', id='stop-measuring', n_clicks=0, style={'margin-left': '10px'}),
                    html.Div(id='sensor-status', style={'margin-left': '20px', 'margin-right': 'auto', 'padding-top': '10px'}),                    
                ]),
                
                html.Div(id='alert-banner', style={'color': 'red', 'font-weight': 'bold', 'margin': '10px', 'padding-left': '10px', 'padding-top': '100px'}),
                dcc.Interval(id='alert-update', interval=2000, n_intervals=0),

            ], width=3),
            # Right Column: Graph and Logs
            dbc.Col([
                # The plot
                dcc.Graph(id='live-graph', animate=False, style={'margin-left': '10px', 'margin-right': '10px', 'border-radius': '25px'}),#,'border': '1px solid blue'}), # borde radius doesn't work to round out borders, doesn't matter tho
                dcc.Interval(
                    id='graph-update',
                    interval=2000,  # in milliseconds
                    n_intervals=0, 
                ),
                html.Hr(),
                html.Div([
                    #html.H4('Sensor Logs'),
                    html.Div([
                        html.H4('Sensor Logs'),
                        html.Button('Detailed Logs', id='detailed-logs', n_clicks=0)
                    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'padding-left': '0px', 'padding-right': '30px'}),
                    
                    html.Div(id='sensor-logs', style={
                        'whiteSpace': 'pre-line',
                        'maxHeight': '300px',
                        'overflowY': 'scroll',
                        'border': '1px solid #ccc',
                        'padding': '10px',
                        #'backgroundColor': '#f9f9f9'
                        'backgroundColor': '#000000',
                        'margin-right': '20px'
                    }),
                    dcc.Interval(id='log-update', interval=2000, n_intervals=0),
                ]),
            ], width=9),
        ]),
    ])

def build_tab2() -> html.Div:
    """
    Builds the second tab in the main application layout.

    Returns
    -------
    html.Div
        A Dash component representing the second tab's content.
    """
    return html.Div([
        html.H3('Specification Settings', style={'margin-left': '10px'}),
        html.Div([
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Sensor Name'),
                        html.Th('Upper Control Limit (UCL)'),
                        html.Th('Lower Control Limit (LCL)'),
                        html.Th(''),
                    ])
                ]),
                html.Tbody([
                    # Row for Temperature Sensor
                    html.Tr([
                        html.Td('Temperature Sensor'),
                        html.Td(dcc.Input(
                            id='temp-ucl',
                            type='number',
                            value=temperature_sensor.ucl,
                            style={'width': '100px'}
                        )),
                        html.Td(dcc.Input(
                            id='temp-lcl',
                            type='number',
                            value=temperature_sensor.lcl,
                            style={'width': '100px'}
                        )),
                        html.Td(html.Button('Update Limits', id='update-temp-limits', n_clicks=0)),
                    ]),
                    # Row for Pressure Sensor
                    html.Tr([
                        html.Td('Pressure Sensor'),
                        html.Td(dcc.Input(
                            id='pressure-ucl',
                            type='number',
                            value=pressure_sensor.ucl,
                            style={'width': '100px'}
                        )),
                        html.Td(dcc.Input(
                            id='pressure-lcl',
                            type='number',
                            value=pressure_sensor.lcl,
                            style={'width': '100px'}
                        )),
                        html.Td(html.Button('Update Limits', id='update-pressure-limits', n_clicks=0)),
                    ]),
                    # Row for Radiation Sensor
                    html.Tr([
                        html.Td('Radiation Sensor'),
                        html.Td(dcc.Input(
                            id='radiation-ucl',
                            type='number',
                            value=radiation_sensor.ucl,
                            style={'width': '100px'}
                        )),
                        html.Td(dcc.Input(
                            id='radiation-lcl',
                            type='number',
                            value=radiation_sensor.lcl,
                            style={'width': '100px'}
                        )),
                        html.Td(html.Button('Update Limits', id='update-radiation-limits', n_clicks=0)),
                    ]),
                ])
            ]),
        ], style={'margin': '20px'}),
        html.Div(id='update-limits-output', style={'color': 'green', 'margin': '20px'}),
    ])


def build_tab3() -> html.Div:
    """
    Builds the third tab of the application, which contains the experiment controls.

    Returns:
        html.Div: The third tab of the application
    """
    return html.Div([
        html.H3("Experiment Control", style={'margin-left': '10px'}),

        # Experiment 1 Controls
        html.Div([
            html.Div("Experiment 1: Temperature", style={'display': 'inline-block', 'fontSize': 24, 'width': '49%', 'margin-left': '10px'}),
            html.Div([
                html.Button('Start', id='start-experiment1', n_clicks=0, style={'margin-right': '5px'}),
                html.Button('Stop', id='stop-experiment1', n_clicks=0, style={'margin-right': '5px'}),
                html.Button('Inject Bias', id='inject-bias1', n_clicks=0, style={'margin-right': '5px', 'background-color': '#DCDCDC'}),
                html.Button('Simulate Device Failure', id='device-failure1', n_clicks=0, style={'background-color': '#DCDCDC'}),
                # Status indicator
                html.Div(id='status-indicator1', style={
                    'width': '20px', 'height': '20px', 'background-color': 'red',
                    'display': 'inline-block', 'margin-left': '10px'
                }),
            ], style={'display': 'inline-block', 'width': '50%', 'text-align': 'center'}),
        ], style={'width': '100%', 'border': '1px solid #000', 'padding': '10px', 'margin-bottom': '10px'}),

        # Experiment 2 Controls
        html.Div([
            html.Div("Experiment 2: Pressure", style={'display': 'inline-block', 'fontSize': 24, 'width': '49%', 'margin-left': '10px'}),
            html.Div([
                html.Button('Start', id='start-experiment2', n_clicks=0, style={'margin-right': '5px'}),
                html.Button('Stop', id='stop-experiment2', n_clicks=0, style={'margin-right': '5px'}),
                html.Button('Inject Bias', id='inject-bias2', n_clicks=0, style={'margin-right': '5px', 'background-color': '#DCDCDC'}),
                html.Button('Simulate Device Failure', id='device-failure2', n_clicks=0, style={'background-color': '#DCDCDC'}),
                # Status indicator
                html.Div(id='status-indicator2', style={
                    'width': '20px', 'height': '20px', 'background-color': 'red',
                    'display': 'inline-block', 'margin-left': '10px'
                }),
            ], style={'display': 'inline-block', 'width': '50%', 'text-align': 'center'}),
        ], style={'width': '100%', 'border': '1px solid #000', 'padding': '10px', 'margin-bottom': '10px'}),

        # Experiment 3 Controls
        html.Div([
            html.Div("Experiment 3: Radiation", style={'display': 'inline-block', 'fontSize': 24, 'width': '49%', 'margin-left': '10px'}),
            html.Div([
                html.Button('Start', id='start-experiment3', n_clicks=0, style={'margin-right': '5px'}),
                html.Button('Stop', id='stop-experiment3', n_clicks=0, style={'margin-right': '5px'}),
                html.Button('Inject Bias', id='inject-bias3', n_clicks=0, style={'margin-right': '5px', 'background-color': '#DCDCDC'}),
                html.Button('Simulate Device Failure', id='device-failure3', n_clicks=0, style={'background-color': '#DCDCDC'}),
                # Status indicator
                html.Div(id='status-indicator3', style={
                    'width': '20px', 'height': '20px', 'background-color': 'red',
                    'display': 'inline-block', 'margin-left': '10px'
                }),
            ], style={'display': 'inline-block', 'width': '50%', 'text-align': 'center'}),
        ], style={'width': '100%', 'border': '1px solid #000', 'padding': '10px', 'margin-bottom': '10px'}),


        # Terminal log
        html.H3("Log", style={'margin-left': '10px'}),
        html.Div(id='terminal_experiment', style={
            'whiteSpace': 'pre-line', 'border': '1px solid white', 'padding': '10px', 'margin-left': '20px', 'margin-right': '20px',
            'height': '300px', 'overflowY': 'scroll', 'backgroundColor': '#000000'
        }),
    ])


# Top of Page --------------------------------------------------------------------------------------

# Callback to render the content of each tab __________________________________________________
@app.callback(
    Output("app-content", "children"),
    Input("app-tabs", "value"),
)
def render_tab_content(
    tab_switch: str  # The value of the dcc.Tabs component
) -> html.Div:
    """
    Render the content based on the currently selected tab.

    Args:
        tab_switch (str): The value of the dcc.Tabs component.

    Returns:
        html.Div: The content of the selected tab.
    """
    if tab_switch == "tab1":
        return build_tab1()
    elif tab_switch == "tab2":
        return build_tab2()
    elif tab_switch == "tab3":
        return build_tab3()
    

# ======= Callbacks for modal popup =======
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks_timestamp"),
     Input("markdown_close", "n_clicks_timestamp"),
     Input("markdown", "n_clicks_timestamp")],
    [State("markdown", "style")]
)
def display_modal(
    open_ts: Optional[int],
    close_ts: Optional[int],
    background_ts: Optional[int],
    style: Dict[str, str]
) -> Dict[str, str]:
    """
    Display the modal popup based on the most recent click event.

    Args:
        open_ts (Optional[int]): Timestamp of the "Learn More" button click.
        close_ts (Optional[int]): Timestamp of the "Close" button click.
        background_ts (Optional[int]): Timestamp of the background click.
        style (Dict[str, str]): The style of the modal popup.

    Returns:
        Dict[str, str]: The updated style of the modal popup.
    """
    if open_ts is None:
        open_ts = 0
    if close_ts is None:
        close_ts = 0
    if background_ts is None:
        background_ts = 0

    if int(open_ts) > max(int(close_ts), int(background_ts)):
        return {"display": "block"}
    elif int(close_ts) > max(int(open_ts), int(background_ts)):
        return {"display": "none"}
    elif int(background_ts) > max(int(open_ts), int(close_ts)):
        return {"display": "none"}
    else:
        return style


# Specification tab ---------------------------------------------------------------------------------

# Callback to handle limit updates _______________________________________________________________
@app.callback(
    Output('update-limits-output', 'children'),
    [Input('update-temp-limits', 'n_clicks'),
     Input('update-pressure-limits', 'n_clicks'),
     Input('update-radiation-limits', 'n_clicks')],
    [State('temp-ucl', 'value'),
     State('temp-lcl', 'value'),
     State('pressure-ucl', 'value'),
     State('pressure-lcl', 'value'),
     State('radiation-ucl', 'value'),
     State('radiation-lcl', 'value')]
)
def update_limits(
    temp_n_clicks: int,
    pressure_n_clicks: int,
    radiation_n_clicks: int,
    temp_ucl: float,
    temp_lcl: float,
    pressure_ucl: float,
    pressure_lcl: float,
    radiation_ucl: float,
    radiation_lcl: float
) -> str:
    """
    Update the limits for the given sensor based on the most recent button click.

    Args:
        temp_n_clicks (int): Number of times the "Update Temp Limits" button was clicked.
        pressure_n_clicks (int): Number of times the "Update Pressure Limits" button was clicked.
        radiation_n_clicks (int): Number of times the "Update Radiation Limits" button was clicked.
        temp_ucl (float): Upper control limit for the temperature sensor.
        temp_lcl (float): Lower control limit for the temperature sensor.
        pressure_ucl (float): Upper control limit for the pressure sensor.
        pressure_lcl (float): Lower control limit for the pressure sensor.
        radiation_ucl (float): Upper control limit for the radiation sensor.
        radiation_lcl (float): Lower control limit for the radiation sensor.

    Returns:
        str: A message indicating which sensor limits were updated. If no limits were updated, an empty string is returned.
    """
    ctx = dash.callback_context

    if not ctx.triggered:
        return ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'update-temp-limits' and temp_n_clicks:
        temperature_sensor.ucl = temp_ucl
        temperature_sensor.lcl = temp_lcl
        return 'Temperature sensor limits updated.'
    elif button_id == 'update-pressure-limits' and pressure_n_clicks:
        pressure_sensor.ucl = pressure_ucl
        pressure_sensor.lcl = pressure_lcl
        return 'Pressure sensor limits updated.'
    elif button_id == 'update-radiation-limits' and radiation_n_clicks:
        radiation_sensor.ucl = radiation_ucl
        radiation_sensor.lcl = radiation_lcl
        return 'Radiation sensor limits updated.'
    return ''


# DASHBOARD -----------------------------------------------------------------------------------------

def get_status_color(status: str) -> str:
    """
    Given a sensor status, return the corresponding color as a string.

    Args:
        status (str): The status of the sensor, one of 'off', 'on', 'measuring', or 'idle'.

    Returns:
        str: The color of the sensor as a string, one of 'red', 'green', 'blue', 'orange', or 'black'.
    """
    if status == 'off':
        return 'red'
    elif status == 'on':
        return 'green'
    elif status == 'measuring':
        return 'blue'
    elif status == 'idle':
        return 'orange'
    else:
        return 'black'


# Callback to control the sensor ______________________________________________________________________
@app.callback(
    Output('sensor-status', 'children'),
    [Input('start-sensor', 'n_clicks'),
     Input('stop-sensor', 'n_clicks'),
     Input('start-measuring', 'n_clicks'),
     Input('stop-measuring', 'n_clicks'),
     Input('detailed-logs', 'n_clicks'),
     Input('device-selector', 'value')]
)
def control_sensor(
    start_sensor: int,
    stop_sensor: int,
    start_measuring: int,
    stop_measuring: int,
    detailed_logs_clicks: int,
    device_name: str
) -> html.Span:
    """
    Control the sensor based on the user input.

    Args:
        start_sensor (int): Number of times the "Start Sensor" button was clicked.
        stop_sensor (int): Number of times the "Stop Sensor" button was clicked.
        start_measuring (int): Number of times the "Start Measuring" button was clicked.
        stop_measuring (int): Number of times the "Stop Measuring" button was clicked.
        device_name (str): Name of the device selected by the user.

    Returns:
        html.Span: A color-coded Span element with the current sensor status.
    """
    details = sensor_details[device_name]
    current_sensor = details['sensor']

    ctx = dash.callback_context
    if not ctx.triggered:
        # Color-coded status
        status = current_sensor.state.value
        color = get_status_color(status)
        return html.Span(f"Sensor Status: {status}", style={'color': color})
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'start-sensor':
        current_sensor.start()
    elif button_id == 'stop-sensor':
        current_sensor.stop()
    elif button_id == 'start-measuring':
        if current_sensor.state in (current_sensor.state.ON, current_sensor.state.IDLE):
            current_sensor.start_measuring()
    elif button_id == 'stop-measuring':
        current_sensor.stop_measuring()
    elif button_id == 'detailed-logs':
        current_sensor.change_loglogs()

    # Color-coded status
    status = current_sensor.state.value
    color = get_status_color(status)
    return html.Span(f"Sensor Status: {status}", style={'color': color})


# Callback to update the live graph __________________________________________________________________
from plotly.subplots import make_subplots

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals'),
     Input('device-selector', 'value'),
     Input('time-interval', 'value')]
)
def update_graph_live(
    n: int,  # Number of times the update interval has passed
    device_name: str,  # Name of the selected device
    time_interval: str  # Selected time interval
) -> go.Figure:
    """
    Updates the live graph with the latest data from the database.

    Args:
        n (int): Number of times the update interval has passed.
        device_name (str): Name of the selected device.
        time_interval (str): Selected time interval.

    Returns:
        go.Figure: The updated graph figure.
    """
    #current_sensor, data_column, yaxis_title = current_sensor_device_name(device_name)
    details = sensor_details[device_name]
    current_sensor = details['sensor']
    data_column = details['data_column']
    yaxis_title = details['xaxis_title']

    # Get control limits from the sensor object
    ucl = current_sensor.ucl
    lcl = current_sensor.lcl

    # Map time_interval to time delta ___________________________________
    time_deltas = {
        '5min': '5 minutes',
        '15min': '15 minutes',
        '1h': '1 hour',
        '12h': '12 hours',
        '1d': '1 day',
        '5d': '5 days',
        '1M': '1 month'
    }
    time_delta = time_deltas[time_interval]

    # Monitoring service ________________________________________________
    
    # Build the query to get data within the time interval
    table_name = f"{current_sensor.name}_measurements"
    query = f"""
        SELECT * FROM {table_name}
        WHERE timestamp_measured >= NOW() - INTERVAL '{time_delta}'
        ORDER BY timestamp_measured ASC
    """
    df = pd.read_sql_query(query, db_engine)

    monitoring_service = MonitoringService(current_sensor)

    # Check for device failure
    warnings = monitoring_service.check_device_failure(df)

    if df.empty:
        # Log warnings
        for warning in warnings:
            current_sensor.log_warning(warning)
        return go.Figure()

    # Check for out-of-control points
    out_of_control_warnings = monitoring_service.check_out_of_control(df, data_column)
    warnings.extend(out_of_control_warnings)

    # Log warnings
    for warning in warnings:
        current_sensor.log_warning(warning)

    # Create subplots __________________________________________________
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                        column_widths=[0.7, 0.3],
                        horizontal_spacing=0.02)

    # Set marker colors based on control limits
    colors = ['red' if y > current_sensor.ucl or y < current_sensor.lcl else 'blue' for y in df[data_column]]

    # Main time-series plot
    fig.add_trace(
        go.Scatter(
            x=df['timestamp_measured'],
            y=df[data_column],
            mode='lines+markers',
            name=data_column.capitalize(),
            marker=dict(color=colors)
        ),
        row=1, col=1
    )

    # Lines for control limits
    fig.add_trace(
        go.Scatter(
            x=[df['timestamp_measured'].iloc[0], df['timestamp_measured'].iloc[-1]],
            y=[ucl, ucl],
            mode='lines',
            name='UCL',
            line=dict(color='red', dash='dash')
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=[df['timestamp_measured'].iloc[0], df['timestamp_measured'].iloc[-1]],
            y=[lcl, lcl],
            mode='lines',
            name='LCL',
            line=dict(color='red', dash='dash')
        ),
        row=1, col=1
    )

    # Rotated histogram plot
    fig.add_trace(
        go.Histogram(
            y=df[data_column],
            nbinsy=20,
            name='Distribution',
            orientation='h',
            showlegend=False
        ),
        row=1, col=2
    )

    fig.update_layout(
        title=f'{device_name.replace("_", " ").title()} Over Time',
        xaxis=dict(title='Time'),
        yaxis=dict(title=yaxis_title),
        bargap=0.1,
        hovermode='closest',
        showlegend=True,
    )

    return fig

# Callback to update the distribution graph __________________________________________________
@app.callback(
    Output('distribution-graph', 'figure'),
    [Input('graph-update', 'n_intervals'),  # type: int
     Input('device-selector', 'value')]  # type: str
)
def update_distribution(n: int, device_name: str) -> go.Figure:
    """
    Callback to update the distribution graph.

    Reads the data from the database using the selected device's name and
    returns a Figure object with a histogram of the data.

    Parameters
    ----------
    n : int
        The number of intervals since the last update.
    device_name : str
        The name of the device to read the data from.

    Returns
    -------
    fig : go.Figure
        A Figure object with a histogram of the data.
    """
    details = sensor_details[device_name]
    current_sensor = details['sensor']
    data_column = details['data_column']
    xaxis_title = details['xaxis_title']

    # Read data from the database
    table_name = f"{current_sensor.name}_measurements"
    query = f"""
        --beginsql
        SELECT * FROM {table_name}
        --endsql
        """
    df = pd.read_sql_query(query, db_engine)

    if df.empty:
        return go.Figure()

    hist = go.Histogram(
        x=df['temperature'],
        nbinsx=20,
        name='Temperature Distribution'
    )

    layout = go.Layout(
        title='Temperature Distribution',
        xaxis=dict(title='Temperature (°C)'),
        yaxis=dict(title='Count'),
    )

    fig = go.Figure(data=[hist], layout=layout)
    return fig

# Callback to update the logs ______________________________________________________________________
@app.callback(
    Output('sensor-logs', 'children'),
    [Input('log-update', 'n_intervals'),
     Input('device-selector', 'value')]
)
def update_logs(n_intervals: int, device_name: str) -> str:
    """
    Updates the logs on the page based on the selected device and the interval.

    Parameters
    ----------
    n_intervals : int
        The number of times the interval has passed.
    device_name : str
        The name of the device to show logs for.

    Returns
    -------
    str
        The text of the logs to display.
    """
    details = sensor_details[device_name]
    current_sensor = details['sensor']

    logs = '\n'.join(current_sensor.get_logs()[-10:])  # Show last 100 logs
    return logs


# Callback to update the alert banner ______________________________________________________________
@app.callback(
    Output('alert-banner', 'children'),  # Output: String
    [Input('alert-update', 'n_intervals'),  # Input: Number of times the interval has passed
     Input('device-selector', 'value')]  # Input: String device name
)
def update_alert(n_intervals: int, device_name: str) -> str:
    """
    Updates the alert banner based on the selected device and the interval.

    Parameters
    ----------
    n_intervals : int
        The number of times the interval has passed.
    device_name : str
        The name of the device to show logs for.

    Returns
    -------
    str
        The text of the alert banner to display.
    """
    details = sensor_details[device_name]
    current_sensor = details['sensor']

    # Get the latest warnings
    recent_logs = current_sensor.get_logs()[-5:]  # Get last 5 logs
    warnings = [log for log in recent_logs if 'WARNING' in log]

    if warnings:
        return 'ALERT: ' + warnings[-1]  # Display the latest warning
    else:
        return ''


# Experiments -------------------------------------------------------------------------------

# Callback to control the experiments __________________________________________________________
@app.callback(
    [Output('terminal_experiment', 'children'),
     Output('experiment1-state', 'data'),
     Output('experiment2-state', 'data'),
     Output('experiment3-state', 'data')],
    [Input('start-experiment1', 'n_clicks'),
     Input('stop-experiment1', 'n_clicks'),
     Input('inject-bias1', 'n_clicks'),
     Input('device-failure1', 'n_clicks'),
     Input('start-experiment2', 'n_clicks'),
     Input('stop-experiment2', 'n_clicks'),
     Input('inject-bias2', 'n_clicks'),
     Input('device-failure2', 'n_clicks'),
     Input('start-experiment3', 'n_clicks'),
     Input('stop-experiment3', 'n_clicks'),
     Input('inject-bias3', 'n_clicks'),
     Input('device-failure3', 'n_clicks')],
    [State('experiment1-state', 'data'),
     State('experiment2-state', 'data'),
     State('experiment3-state', 'data')]
)
def control_experiments(
        start1: int, stop1: int, inject_bias1: int, device_failure1: int,
        start2: int, stop2: int, inject_bias2: int, device_failure2: int,
        start3: int, stop3: int, inject_bias3: int, device_failure3: int,
        state1: dict, state2: dict, state3: dict) -> Tuple[str, dict, dict, dict]:
    """
    Controls the experiments based on button clicks.

    Parameters
    ----------
    start1 : int
        Number of times the start button for experiment 1 was clicked.
    stop1 : int
        Number of times the stop button for experiment 1 was clicked.
    inject_bias1 : int
        Number of times the bias injection button for experiment 1 was clicked.
    device_failure1 : int
        Number of times the device failure button for experiment 1 was clicked.
    start2 : int
        Number of times the start button for experiment 2 was clicked.
    stop2 : int
        Number of times the stop button for experiment 2 was clicked.
    inject_bias2 : int
        Number of times the bias injection button for experiment 2 was clicked.
    device_failure2 : int
        Number of times the device failure button for experiment 2 was clicked.
    start3 : int
        Number of times the start button for experiment 3 was clicked.
    stop3 : int
        Number of times the stop button for experiment 3 was clicked.
    inject_bias3 : int
        Number of times the bias injection button for experiment 3 was clicked.
    device_failure3 : int
        Number of times the device failure button for experiment 3 was clicked.
    state1 : dict
        State dictionary for experiment 1.
    state2 : dict
        State dictionary for experiment 2.
    state3 : dict
        State dictionary for experiment 3.

    Returns
    -------
    str
        Log messages for the experiment control.
    dict
        Updated state dictionary for experiment 1.
    dict
        Updated state dictionary for experiment 2.
    dict
        Updated state dictionary for experiment 3.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return "", state1, state2, state3  # No changes

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    log = ""

    # Ensure state dictionaries are mutable copies
    state1 = state1.copy()
    state2 = state2.copy()
    state3 = state3.copy()

    # Experiment 1 controls
    if button_id in ['start-experiment1', 'stop-experiment1', 'inject-bias1', 'device-failure1']:
        if button_id == 'start-experiment1':
            threading.Thread(target=experiment1.run_experiment).start()
            log += "Experiment 1 started.\n"
            state1['running'] = True
            # Do not change bias or failure flags
        elif button_id == 'stop-experiment1':
            experiment1.exp.stop_experiment()
            log_message = get_log_message(experiment1.log_queue)
            log += f"{log_message}\n"
            state1['running'] = False
            state1['bias'] = False
            state1['failure'] = False
        elif button_id == 'inject-bias1':
            experiment1.exp.toggle_bias()
            log_message = get_log_message(experiment1.log_queue)
            log += f"{log_message}\n"
            state1['bias'] = not state1.get('bias', False)
        elif button_id == 'device-failure1':
            experiment1.exp.toggle_device_failure()
            log_message = get_log_message(experiment1.log_queue)
            log += f"{log_message}\n"
            state1['failure'] = not state1.get('failure', False)

    # Experiment 2 controls
    if button_id in ['start-experiment2', 'stop-experiment2', 'inject-bias2', 'device-failure2']:
        if button_id == 'start-experiment2':
            threading.Thread(target=experiment2.run_experiment).start()
            log += "Experiment 2 started.\n"
            state2['running'] = True
            # Do not change bias or failure flags
        elif button_id == 'stop-experiment2':
            experiment2.exp.stop_experiment()
            log_message = get_log_message(experiment2.log_queue)
            log += f"{log_message}\n"
            state2['running'] = False
            state2['bias'] = False
            state2['failure'] = False
        elif button_id == 'inject-bias2':
            experiment2.exp.toggle_bias()
            log_message = get_log_message(experiment2.log_queue)
            log += f"{log_message}\n"
            state2['bias'] = not state2.get('bias', False)
        elif button_id == 'device-failure2':
            experiment2.exp.toggle_device_failure()
            log_message = get_log_message(experiment2.log_queue)
            log += f"{log_message}\n"
            state2['failure'] = not state2.get('failure', False)

    # Experiment 3 controls
    if button_id in ['start-experiment3', 'stop-experiment3', 'inject-bias3', 'device-failure3']:
        if button_id == 'start-experiment3':
            threading.Thread(target=experiment3.run_experiment).start()
            log += "Experiment 3 started.\n"
            state3['running'] = True
            # Do not change bias or failure flags
        elif button_id == 'stop-experiment3':
            experiment3.exp.stop_experiment()
            log_message = get_log_message(experiment3.log_queue)
            log += f"{log_message}\n"
            state3['running'] = False
            state3['bias'] = False
            state3['failure'] = False
        elif button_id == 'inject-bias3':
            experiment3.exp.toggle_bias()
            log_message = get_log_message(experiment3.log_queue)
            log += f"{log_message}\n"
            state3['bias'] = not state3.get('bias', False)
        elif button_id == 'device-failure3':
            experiment3.exp.toggle_device_failure()
            log_message = get_log_message(experiment3.log_queue)
            log += f"{log_message}\n"
            state3['failure'] = not state3.get('failure', False)

    # Print expected values
    log += "\nExpected Generated Data:\n"
    log += f"Experiment 1: {{Temperature mean: {experiment1.exp.mean} °C, stddev: {experiment1.exp.stddev} °C, bias: {experiment1.exp.bias} °C}}\n"
    log += f"Experiment 2: {{Pressure mean: {experiment2.exp.mean} bar, stddev: {experiment2.exp.stddev} bar, bias: {experiment2.exp.bias} bar}}\n"
    log += f"Experiment 3: {{Temperature mean: {experiment3.exp.mean} mSv/h, stddev: {experiment3.exp.stddev} mSv/h, bias: {experiment3.exp.bias} mSv/h}}\n"

    return log, state1, state2, state3


# Callback to control the experiments states ___________________________________________________
@app.callback(
    [Output('status-indicator1', 'style'),
     Output('status-indicator2', 'style'),
     Output('status-indicator3', 'style')],
    [Input('experiment1-state', 'data'),
     Input('experiment2-state', 'data'),
     Input('experiment3-state', 'data')]
)
def update_status_indicators(
        state1: Dict[str, bool], state2: Dict[str, bool], state3: Dict[str, bool]
    ) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """
    Update the status indicator colors based on the experiment states.

    Args:
        state1 (Dict[str, bool]): Experiment 1 state.
        state2 (Dict[str, bool]): Experiment 2 state.
        state3 (Dict[str, bool]): Experiment 3 state.

    Returns:
        Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]: Status indicator styles.
    """
    def get_style(state: Dict[str, bool]) -> Dict[str, str]:
        """
        Get the status indicator style based on the experiment state.

        Args:
            state (Dict[str, bool]): Experiment state.

        Returns:
            Dict[str, str]: Status indicator style.
        """
        if not state.get('running', False):
            color = 'red'  # Experiment is stopped
        elif state.get('failure', False):
            color = 'purple'
        elif state.get('bias', False):
            color = 'orange'
        else:
            color = 'green'
        return {
            'width': '20px',
            'height': '20px',
            'background-color': color,
            'display': 'inline-block',
            'margin-left': '10px'
        }

    style1 = get_style(state1)
    style2 = get_style(state2)
    style3 = get_style(state3)
    return style1, style2, style3



if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0', port=8050, debug=True)



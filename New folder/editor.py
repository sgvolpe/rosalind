import base64
import io
import json
import logging
import os
from datetime import date
from datetime import datetime
from urllib.parse import parse_qs

import dash
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, State, callback
from dash import html
from dash import no_update
from dash.dependencies import ALL

from app.core.config import STATIC_PATH
from dashboards.pages import read_cookie
from schemas.components.buttons import debug_button, edit_button, show_chart_settings_button, generate_pdf_button
from schemas.components.header import Header
from schemas.components.scroll_to_top import scroll_to_top
from schemas.custom_report import CustomReport
from schemas.custom_report.cards import Cards as kpi_cards

report_name = "Report Editor"
dash.register_page(
    __name__,
    path="/editor",
    name=report_name,
    title=report_name,
)

empty_page = html.Div(
    id="empty-page-div",
    children=[
        dbc.Container(

            children=[
                html.H1("No Content.", className="display-3"),
                html.P(
                    "Use one of the functionalities to start building your report.",
                    className="lead",
                ),
                html.Hr(className="my-2"),

                dbc.Row(
                    children=[
                        dbc.Col(
                            dbc.Button('Start New Report', className="spark-btn spark-btn--sm",
                                       id="start-new-report-btn")),
                        dbc.Col(dbc.Button('Load Existing Report', className="spark-btn spark-btn--sm"
                                           , id="load-existing-report-btn")),
                        dbc.Col(
                            dbc.Button('Upload Report from File', className="spark-btn spark-btn--sm"
                                       , id="upload-report-file-btn")
                        ),
                    ],

                    className="lead"),
            ],
            fluid=True,
            className="py-3",
        )
    ],
    className="p-3 bg-body-secondary rounded-3 spark-mar-2",
    style={"max-width": "1200px", "margin": "auto"},
)


def get_method_path_for_card(card):
    """Return the full import path for a function or method reference."""
    func = card.method
    return f"{func.__module__}.{func.__qualname__}"


cards = [
    kpi_cards.Chart.FailureRate.by_date,
    kpi_cards.Chart.FailureRate.failure_rate_by_date,
    kpi_cards.Chart.FailureRate.by_date_per_airline,
    kpi_cards.Chart.FailureRate.by_date_per_pcc,
    kpi_cards.Chart.ShoppingRequests.by_date,
    kpi_cards.Chart.ShoppingRequests.by_date_with_title,
    kpi_cards.Chart.ShoppingRequests.by_date_with_title,
    kpi_cards.Chart.L2B.by_date,
    kpi_cards.Chart.L2B.rqs_and_l2b,
    kpi_cards.Chart.L2B.l2b_by_date_per_pcc,
    kpi_cards.Chart.L2B.bookings_by_date,
    kpi_cards.Chart.L2B.bookings_by_date_with_title,
    kpi_cards.Chart.L2B.bookings_by_date_with_title,
    kpi_cards.Chart.L2B.number_of_itineraries,
    kpi_cards.Chart.EmptyResponses.by_date_per_pcc,
    kpi_cards.Chart.EmptyResponses.by_date,
    kpi_cards.Chart.ResponseTime.by_date,
    kpi_cards.Chart.ResponseTime.count_by_bucket__date,
    kpi_cards.Chart.ResponseTime.by_date__bucket_per_service,
    kpi_cards.Chart.Services.number_of_itins_per_date__service,

]

cards_index = {
    card.uid: card for card in cards
}
components = {
    card.uid: {
        "method": get_method_path_for_card(card),
        "uid": card.uid,
    } for card in cards
}


def empty_tab(idx=0, title: str = None) -> dict:
    return {
        'title': title or f'Tab {idx + 1}',
        'children': [
            empty_row(idx=0, tab_idx=idx),
        ]
    }


def empty_row(idx=0, tab_idx=0) -> dict:
    return {
        'type': 'row',
        'children': [
            empty_col(idx=0, row_idx=idx, tab_idx=tab_idx),

        ]
    }


def empty_col(idx=0, tab_idx=0, row_idx=0) -> dict:
    logging.debug("CREATING EMPTY COL")

    return {
        'type': 'col',
        'children': [
            # empty_card(idx, col_idx=idx, tab_idx=tab_idx, row_idx=row_idx),
        ]
    }


def empty_card(idx=0, col_idx=0, tab_idx=0, row_idx=0) -> dict:
    return {
        'type': 'card',
        'title': f'EMPTY Card {idx + 1}',
        'footer': None,
        'children': None,
        "idx": idx,
        "col_idx": col_idx,
        "tab_idx": tab_idx,
        "row_idx": row_idx,
    }


def render_card(card, idx, tab_idx, row_idx, col_idx, search_dict) -> list:
    logging.debug(f"         RENDERING CARD {idx} ")
    logging.debug(f'        {card=}')
    logging.debug(f'{card=}')
    if card.get("method", False):
        card_component = cards_index.get(card.get("uid"))

        return card_component.as_dash(**search_dict)

    return [
        dbc.Card(
            [
                dbc.CardHeader([
                    card.get('title', "Untitled Card"),
                ]),
                dbc.CardBody([
                    card.get('children', "No Content")
                ]),
                dbc.CardFooter([
                    card.get('footer', "No Footer")
                ])
            ])
    ]


def render_col(col, col_idx, tab_idx, row_idx, search_dict, width=12) -> dbc.Col:
    logging.debug(f"RENDERING COL {col_idx}")
    logging.debug(f'        {col=}')
    rendered_card = None
    col_children = col.get('children', [])
    if len(col_children) > 0:
        for idx, child in enumerate(col_children):
            add_component_style = {"display": "none", "marginTop": "10px", "marginBottom": "10px"}
            if isinstance(child, dict) and child.get('type') == 'card':
                rendered_card = render_card(child, idx, tab_idx, row_idx, col_idx, search_dict)
            else:
                rendered_card = str(child)
    else:
        add_component_style = {"display": "block", "marginTop": "10px", "marginBottom": "10px"}
    add_component_row = dbc.Row(
        id={
            "type": "add-component-row",
            "col_idx": col_idx, "tab_idx": tab_idx, "row_idx": row_idx
        },
        children=dbc.Col(
            dbc.InputGroup(
                [
                    dcc.Dropdown(
                        id={
                            "type": "component-dropdown",
                            "tab": tab_idx,
                            "row": row_idx,
                            "col": col_idx
                        },
                        options=[{"label": k, "value": k} for k in components.keys()],
                        placeholder="Select component",
                        className="report-dropdown"
                    ),
                    dbc.Button(
                        "Add",
                        id={
                            "type": "add-component-btn",
                            "tab": tab_idx,
                            "row": row_idx,
                            "col": col_idx
                        },
                        className="spark-btn spark-btn--sm"
                    ),
                ],
            ),
        ),
        align="center",
        className="add-component-row",
        style=add_component_style
    )

    remove_button = dbc.Button(
        "Remove Column",
        id={"type": "remove-col-btn", "tab": tab_idx, "row": row_idx, "col": col_idx},
        className="spark-btn spark-btn--sm spark-btn--negative hover-buttons"
    )

    return dbc.Col(
        [
            dbc.Row(
                dbc.Col(
                    children=rendered_card,
                    className="centered"
                )
            ),
            add_component_row,
            dbc.Row(dbc.Col(remove_button, className="centered hover-col-buttons")),

        ],
        className=""
    )


def render_row(row, row_idx, tab_idx, search_dict) -> dbc.Row:
    logging.debug(f"""
    RENDERING ROW {row_idx}
    {row}
""")
    children = []
    for idx, child in enumerate(row.get('children', [])):
        if isinstance(child, dict) and child.get('type') == 'col':
            children.append(render_col(child, idx, tab_idx, row_idx, search_dict))
        else:
            children.append(str(child))

    children.append(
        dbc.Row(
            dbc.Col(
                children=dbc.Button(
                    "Add Column",
                    id={"type": "add-col-btn", "tab": tab_idx, "row": row_idx},
                    className="spark-btn spark-btn--sm hover-buttons"
                ),
                className="centered",
            ),
            className="spark-mar-1 centered "
        )

    )
    remove_button = dbc.Button(
        "Remove Row",
        id={"type": "remove-row-btn", "tab": tab_idx, "row": row_idx},
        className="spark-btn spark-btn--sm spark-btn--negative"
    )
    children.append(
        dbc.Row(
            dbc.Col(remove_button),
            className="centered hover-buttons"
        )

    )

    return dbc.Row(
        children=children,
        className="spark-mar-1",
    )


def render_tab(tab, tab_idx, search_dict) -> dbc.Tab:
    logging.debug(f"""
    RENDERING TAB {tab_idx}
    {tab.get("uid")=}
    {tab.get("method")=}
    {tab=}
    """)
    children = []
    for idx, child in enumerate(tab.get('children', [])):
        if isinstance(child, dict) and child.get('type') == 'row':
            children.append(
                render_row(
                    child, idx, tab_idx, search_dict
                )
            )
    # Add Row button
    children.append(
        dbc.Row(
            dbc.Col(
                children=[
                    dbc.Button(
                        "Add Row",
                        id={"type": "add-row-btn", "tab": tab_idx},
                        className="spark-btn spark-btn--sm hover-buttons",
                        style={"positon": "relative", "top": "-20px"}
                    )
                ],
                className="centered spark-mar-1"

            ),
            className="add-row-button-row centered spark-mar-1"
        )

    )
    remove_button = dbc.Button(
        "Remove Tab",
        id={"type": "remove-tab-btn", "tab": tab_idx},
        className="spark-btn spark-btn--sm spark-btn--negative"
    )
    children.append(remove_button)
    #
    # return rendered_tab
    return dbc.Tab(
        children=children or ["EMPTY TAB"], label=tab.get('title', f'Tab {tab_idx + 1}'),
        class_name ="spark-tab parent-hover parent-col-hover spark-tabs__panel ", #
        id={"type": "tab", "tab": tab_idx, },
        tab_class_name="tab spark-tabs__tab ",
        tab_style ={"max-width": "100%", "padding": "10px"},
        label_style  ={"max-width": "100%", "padding": "10px"}
    )


def render_tabs(tabs, search_dict) -> dbc.Tabs:
    tabs_children = tabs.get("children", []) if isinstance(tabs, dict) else tabs
    if len(tabs_children) > 0:
        return dbc.Tabs(
           children= [
                render_tab(
                    tab, idx, search_dict
                ) for idx, tab in enumerate(tabs_children)
            ],
        class_name ="", #


        )
    else:
        return "No Tabs Content"


@callback(
    Output('search-dict-store', 'data'),
    Input('url', 'search')

)
def update_search_dict_store(search):
    logging.debug(f"""
    UPDATE SEARCH DICT STORE CALLBACK
    {search=}
    """)
    search_dict = {k: v[0] for k, v in parse_qs(search.lstrip('?')).items()}
    logging.debug(f'{search_dict=}')
    return search_dict


@callback(
    Output('tabs-container', 'children'),
    Output('report-title', 'value'),
    Output('author-name', 'value'),
    Output('report-date', 'value'),
    Output('description', 'value'),
    [
        Input('report-config', 'data'),
        Input('url', 'search')
    ],
    prevent_initial_call=True

)
def update_tabs(data, search):
    logging.debug(f"""
    UPDATE TABS CALLBACK
    {data=}
    {search=}
    """)
    search_dict = {k: v[0] for k, v in parse_qs(search.lstrip('?')).items()}
    return (
        render_tabs(
            data.get('tabs', []),
            search_dict
        ),
        data.get('title', ''),
        data.get('author', ''),
        data.get('date', str(date.today())),
        data.get('description', '')
    )


@callback(
    Output('save-output', 'children'),
    Input('preview-config', 'n_clicks'),
    State('report-title', 'value'),
    State('author-name', 'value'),
    State('report-date', 'date'),
    State('description', 'value'),
    State('report-config', 'data'),
    prevent_initial_call=True
)
def save_config(n, title, author, date_val, desc, data):
    data['title'] = title
    data['author'] = author
    data['date'] = date_val
    data['description'] = desc
    json_str = json.dumps(data, indent=2)
    return dcc.Textarea(value=json_str, style={'width': '100%', 'height': '300px'})


@callback(
    Output('messages-div', 'children'),
    Input('save-config', 'n_clicks'),
    State('report-title', 'value'),
    State('author-name', 'value'),
    State('report-date', 'date'),
    State('description', 'value'),
    State('report-config', 'data'),
    prevent_initial_call=True
)
def save_config_to_folder(n, title, author, date_val, desc, data):
    if not n:
        return no_update
    data['title'] = title
    data['author'] = author
    data['date'] = date_val
    data['description'] = desc
    # Create folder if not exists
    save_dir = STATIC_PATH / 'report_configurations'
    os.makedirs(save_dir, exist_ok=True)
    # Use title and date for filename, fallback to timestamp if missing
    safe_title = (title or 'untitled').replace(' ', '_')
    safe_date = date_val or datetime.now().strftime('%Y-%m-%d')
    filename = f"{safe_title}_{safe_date}.json"
    save_path = save_dir / filename
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return f"Saved to {save_path}"  # Or return a dcc.Textarea/json preview if you prefer


@callback(
    Output('report-config', 'data', allow_duplicate=True),
    [
        Input('add-tab-btn', 'n_clicks'),
        Input({'type': 'add-row-btn', 'tab': ALL}, 'n_clicks'),
        Input({'type': 'add-col-btn', 'tab': ALL, 'row': ALL}, 'n_clicks'),
        Input({'type': 'add-component-btn', 'tab': ALL, 'row': ALL, 'col': ALL}, 'n_clicks'),
        Input('upload-config', 'contents'),
        Input('load-btn', 'n_clicks'),
        Input('existing-configurations', 'value'),
        State('new-tab-title', 'value'),
        Input({'type': 'remove-col-btn', 'tab': ALL, "row": ALL, "col": ALL}, 'n_clicks'),
        Input({'type': 'remove-row-btn', 'tab': ALL, "row": ALL, }, 'n_clicks'),
        Input({'type': 'remove-tab-btn', 'tab': ALL}, 'n_clicks'),

    ],
    [
        State({'type': 'component-dropdown', 'tab': ALL, 'row': ALL, 'col': ALL}, 'value'),
        State('report-config', 'data'),
        State('upload-config', 'filename'),
    ],
    prevent_initial_call=True
)
def update_report_config(
        add_tab_clicks, add_row_clicks, add_col_clicks, add_comp_clicks, upload_contents, load_config_clicks,
        existing_configurations_value, new_tab_title, remove_col_clicks, remove_row_clicks, remove_tab_clicks,

        # States
        dropdown_values, data, upload_filename,
):
    ctx = dash.callback_context
    if not ctx.triggered or not data:
        return dash.no_update
    trigger = ctx.triggered[0]['prop_id']
    tabs = data.get('tabs', [])

    logging.debug(f'Element Triggered: {trigger=}')
    # Handle upload
    if 'upload-config' in trigger and upload_contents:
        logging.debug("""
        UPLOADING CONFIG
        """)

        content_type, content_string = upload_contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            config = json.load(io.StringIO(decoded.decode('utf-8')))
            return config
        except Exception as e:
            logging.error(f"Error processing uploaded file {upload_filename}: {e}")
            return dash.no_update
    # Add Tab
    if 'add-tab-btn' in trigger:
        n = add_tab_clicks
        if n and (len(tabs) == 0 or n > len(tabs)):
            logging.debug(f'{new_tab_title=}')
            tabs.append(
                empty_tab(idx=len(tabs), title=new_tab_title)
            )
            data['tabs'] = tabs

            return data
    # Add Row
    if 'add-row-btn' in trigger:
        for tab_idx, n in enumerate(add_row_clicks):
            if n and n > 0 and f'add-row-btn' in trigger and f'"tab":{tab_idx}' in trigger:
                tabs[tab_idx]['children'].extend([
                    empty_row(
                        idx=len(tabs[tab_idx]['children']),
                        tab_idx=tab_idx
                    ),
                ]
                )
                data['tabs'] = tabs
                return data
    if "remove-row-btn" in trigger:
        logging.debug(f'{remove_row_clicks=}')
        for tab_idx, tab in enumerate(tabs):
            for row_idx, row in enumerate(tab['children']):
                if row_idx < len(remove_row_clicks) and remove_row_clicks[
                    row_idx] and remove_row_clicks[
                    row_idx] > 0 and f'remove-row-btn' in trigger and f'"tab":{tab_idx}' in trigger and f'"row":{row_idx}' in trigger:
                    tab['children'].pop(row_idx)
                    data['tabs'] = tabs
                    return data
    if "remove-tab-btn" in trigger:
        logging.debug(f'{remove_tab_clicks=}')
        for tab_idx, tab in enumerate(tabs):
            if tab_idx < len(remove_tab_clicks) and remove_tab_clicks[
                tab_idx] and remove_tab_clicks[
                tab_idx] > 0 and f'remove-tab-btn' in trigger and f'"tab":{tab_idx}' in trigger:
                tabs.pop(tab_idx)
                data['tabs'] = tabs
                return data

    # Add Column
    if 'add-col-btn' in trigger:
        idx = 0
        for tab_idx, tab in enumerate(tabs):
            for row_idx, row in enumerate(tab['children']):
                if idx < len(add_col_clicks) and add_col_clicks[idx] and add_col_clicks[
                    idx] > 0 and f'add-col-btn' in trigger and f'"tab":{tab_idx}' in trigger and f'"row":{row_idx}' in trigger:
                    row['children'].append(
                        empty_col(
                            idx=len(row['children']),
                            tab_idx=tab_idx,
                            row_idx=row_idx

                        )
                    )
                    data['tabs'] = tabs
                    return data
                idx += 1

    if 'remove-col-btn' in trigger:
        logging.debug(f'{remove_col_clicks=}')
        idx = 0
        for tab_idx, tab in enumerate(tabs):
            for row_idx, row in enumerate(tab['children']):
                for col_idx, col in enumerate(row['children']):
                    if idx < len(remove_col_clicks) and remove_col_clicks[idx] and remove_col_clicks[
                        idx] > 0 and f'remove-col-btn' in trigger and f'"tab":{tab_idx}' in trigger and f'"row":{row_idx}' in trigger and f'"col":{col_idx}' in trigger:
                        row['children'].pop(col_idx)
                        data['tabs'] = tabs
                        return data
                    idx += 1
    # Add Component
    if 'add-component-btn' in trigger:
        logging.debug(f'{add_comp_clicks=}')
        idx = 0
        for tab_idx, tab in enumerate(tabs):
            logging.debug("PROCESSING TAB", tab_idx)
            for row_idx, row in enumerate(tab['children']):
                logging.debug(" PROCESSING ROW", row_idx)
                for col_idx, col in enumerate(row['children']):
                    logging.debug("  PROCESSING COL", col_idx)
                    logging.debug(f'{idx=} {add_comp_clicks=}')
                    logging.debug(add_comp_clicks[idx])
                    logging.debug(idx < len(add_comp_clicks))
                    logging.debug(f'"tab":{tab_idx}' in trigger)
                    logging.debug(f'"row":{row_idx}' in trigger)
                    logging.debug(f'"col":{col_idx}' in trigger)
                    if (
                            idx < len(add_comp_clicks)
                            and add_comp_clicks[idx]
                            and add_comp_clicks[idx] > 0
                            and f'add-component-btn' in trigger
                            and f'"tab":{tab_idx}' in trigger
                            and f'"row":{row_idx}' in trigger
                            and f'"col":{col_idx}' in trigger
                    ):
                        logging.debug(f'{dropdown_values=}')
                        comp_type = dropdown_values[idx] if dropdown_values and idx < len(dropdown_values) else None
                        logging.debug(f'{comp_type=}')
                        logging.debug(f'{components.get(comp_type, {})=}')
                        if comp_type:
                            col['children'].append(
                                {
                                    'type': 'card',
                                    **components.get(comp_type, {})
                                }
                            )
                            data['tabs'] = tabs
                            return data
                    idx += 1

    if 'load-btn' in trigger:
        with open(STATIC_PATH / 'report_configurations' / existing_configurations_value, 'r') as f:
            config = json.load(f)
            return config
    return dash.no_update


@callback(
    Output('dropdown-options-store', 'data'),
    Input('url', 'pathname'),  # triggers on page load
)
def load_dropdown_options(_):
    directory = 'path/to/your/dir'
    files = os.listdir(directory)
    options = [{"label": f, "value": f} for f in files if not f.startswith('.')]
    return options


# 4. Callback to update dropdown options
@callback(
    Output('example-dropdown', 'options'),
    Input('dropdown-options-store', 'data')
)
def update_dropdown_options(options):
    return options


@callback(
    Output('existing-configurations-store', 'data'),
    Input('url', 'pathname'),
)
def load_existing_configurations(_):
    directory = STATIC_PATH / 'report_configurations'
    files = directory.glob('*.json')

    options = [{"label": f.stem, "value": f.name} for f in files]
    return options


@callback(
    Output('existing-configurations', 'options'),
    Input('existing-configurations-store', 'data')
)
def update_existing_configurations(options):
    return options


@callback(
    Input('generate-pdf-btn', 'n_clicks'),
    State('report-config', 'data'),
    State('search-dict-store', 'data'),

    prevent_initial_call=True
)
def generate_pdf(n_clicks, report_configuration, search_dict):
    logging.debug(f"""
    GENERATING PDF REPORT
    {search_dict=}
    """)

    report = CustomReport(**report_configuration)
    report.as_pdf(**search_dict)


def build_report_form() -> dbc.Container:
    existing_reports = dbc.Container(
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dcc.Dropdown(
                                id='existing-configurations',
                                options=[],
                                placeholder="Select file",
                                style={'width': '100%'}
                            ),

                        ],
                        className="spark-mar-1 centered"
                    ),
                    dbc.Col(

                        dbc.Button('Load Config', id='load-btn',
                                   className="spark-btn spark-btn--sm spark-btn--secondary"),
                    )
                ],
                className="spark-mar-b-2 spark-btn-group spark-btn-group--center"
            ),
        ],
        fluid=True,
        className="report-form-container",
    )
    report_form = dbc.Container(
        children=[
            dbc.Row(
                children=[
                    dbc.Col([
                        dbc.Label('Report Title'),
                        dcc.Input(id='report-title', type='text', style={'width': '100%'})
                    ]),
                    dbc.Col([
                        dbc.Label('Author Name'),
                        dcc.Input(id='author-name', type='text', style={'width': '100%'})
                    ]),
                    dbc.Col([
                        dbc.Label('Report Date'),
                        dcc.DatePickerSingle(id='report-date', date=date.today())
                    ]),
                ],
                className="spark-mar-1"
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            dbc.Label('Description'),
                            dcc.Textarea(id='description', style={'width': '100%'})
                        ]
                    )
                ],
                className="spark-mar-1"
            ),
            dbc.Row(
                [dbc.Col(
                    children=[
                        dbc.Button('Preview Config', id='preview-config', className="spark-btn spark-btn--sm"),

                    ],
                    className="spark-mar-1 centered"
                ),
                    dbc.Col(
                        children=[
                            dbc.Button('Save Config', id='save-config', className="spark-btn spark-btn--sm"),

                        ],
                        className="spark-mar-1 centered"
                    )
                ]
                ,
                className="spark-mar-b-2 spark-btn-group spark-btn-group--center"
            ),
            html.Div(id='save-output'),
        ],
        id="report-form-container",
        fluid=True,
        className="report-form-container",
    )

    drag_form = dbc.Container(
        children=[

            dbc.Row(
                dbc.Col(
                    children=[
                        dcc.Upload(
                            id='upload-config',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A(
                                    'Click to Select a JSON File',
                                    className="spark-link"
                                )
                            ]
                            ),

                            multiple=False,
                            className="spark-mar-1 "
                        )
                    ]
                ),
                className="spark-mar-1 centered"
            )
        ], fluid=True,
        className="report-form-container",
    )
    return [
        dbc.Container(
            children=dbc.Row(
                children=[
                    dbc.Col(
                        id="create-new-report-col",
                        children=[
                            html.H2("Create New Report"),
                            report_form
                        ],
                        className="spark-mar-1 ",
                        style={"display": "none"}
                    ),
                    dbc.Col(
                        id="load-existing-report-col",
                        children=[
                            html.H2("Load Existing Report"),
                            existing_reports
                        ],
                        className="spark-mar-1 ",
                        style={"display": "none"}
                    ),
                    dbc.Col(
                        id="upload-report-col",
                        children=
                        [
                            html.H2("Load from File"),
                            drag_form
                        ],
                        className="spark-mar-1 ",
                        style={"display": "none"}
                    ),

                ]
            ),
            id="combined-report-form-container",
        )
        # report_form, existing_reports, drag_form
    ]


#
# @callback(
#     Output('create-new-report-col', 'style'),
#     Input('create-new-btn', 'n_clicks'),
# )
# def toggle_report_form(n_clicks):
#     if n_clicks and n_clicks % 2 == 1:
#         return {'display': 'block'}
#     return {'display': 'none'}

@callback(
    Output('create-new-report-col', 'style'),
    Output('load-existing-report-col', 'style'),
    Output('upload-report-col', 'style'),
    Input('start-new-report-btn', 'n_clicks'),
    Input('load-existing-report-btn', 'n_clicks'),
    Input('upload-report-file-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_start_new_report_form(a, b, c):
    print("...{{triggered toglge_start_new_report_form}}...")
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    trigger = ctx.triggered[0]['prop_id']

    if 'start-new-report-btn' in trigger and a not in [0, None]:
        return {"display": "block"}, {"display": "none"}, {"display": "none"}
    if 'load-existing-report-btn' in trigger:
        return {"display": "none"}, {"display": "block"}, {"display": "none"}
    if 'upload-report-file-btn' in trigger:
        return {"display": "none"}, {"display": "block"}, {"display": "block"}
    return dash.no_update


#
# @callback(
#     Output('upload-report-col', 'style'),
#     Input('load-existing-report-btn', 'n_clicks'),
# )
# def toggle_load_existing_report_form(n_clicks):
#     if n_clicks and n_clicks % 2 == 1:
#         return {'display': 'block'}
#     return {'display': 'none'}
#
#
# @callback(
#     Output('combined-report-form-container', 'style'),
#     Input('upload-report-file-btn', 'n_clicks'),
# )
# def toggle_upload_report_form(n_clicks):
#     if n_clicks and n_clicks % 2 == 1:
#         return {'display': 'block'}
#     return {'display': 'none'}


def get_store(report_config: dict) -> list:
    print(f'{report_config=}')
    store = [
        dcc.Store(id="configuration_id_store", storage_type="session", data=None),
        dcc.Store(id="debug_store", storage_type="session", data=False),
        dcc.Store(id="date_end_store", storage_type="session", data=None),
        dcc.Store(id="date_start_store", storage_type="session", data=None),
        dcc.Store(id="template_store", storage_type="session", data=None),
        dcc.Store(id="chart_settings_store", storage_type="session", data=None),
        dcc.Store(id="charts_style_store", storage_type="session", data={}),
        dcc.Store(id="template_id_store", storage_type="session", data="vbp"),
        dcc.Store(id='report-config', data=report_config),
        dcc.Store(id='existing-configurations-store', data=[]),
        dcc.Store(id='search-dict-store', data={})

    ]
    return store


def layout(*args, **kwargs):
    try:
        admin_mode, username = read_cookie()
    except Exception as exc:
        return dbc.Container(
            dbc.Row(
                dbc.Col(
                    dbc.Alert(
                        children=[
                            html.H3(f"Error reading cookie: {exc}"),
                        ], color="danger"
                    )
                ), className=""
            )

        )
    action_buttons = [

        *generate_pdf_button,
    ]

    if admin_mode:
        action_buttons.extend(
            [
                *edit_button,
                *show_chart_settings_button,
                *debug_button,
            ]
        )
    navbar = Header(
        action_buttons=action_buttons,
        submit_form=None,
        dialog_is_open=False,
        title=report_name
    ).as_dash()

    messages_div = html.Div(id="messages-div")

    report_id = kwargs.get("report_id")
    logging.debug(f"LOADING REPORT ID {report_id}")

    if report_id is not None:
        logging.debug("REPORT ID IS NOT NONE, LOADING CONFIG")
        # Here you would load the report configuration based on the report_id
        # For example:
        config_path = STATIC_PATH / 'report_configurations' / f'{report_id}.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                report_config = json.load(f)
            logging.debug(f"LOADED REPORT CONFIG: {report_config}")
            form = "READING EXISTING CONFIG"
        else:
            logging.warning(f"CONFIG FILE FOR REPORT ID {report_id} DOES NOT EXIST.")
            report_config = {
                'title': '',
                'author': '',
                'date': str(date.today()),
                'description': '',
                'tabs': []
            }
    else:
        report_config = {
            'title': '',
            'author': '',
            'date': str(date.today()),
            'description': '',
            'tabs': []
        }

    return dbc.Container(
        [
            *scroll_to_top(),
            navbar,
            dbc.Row(
                dbc.Col
                    (
                    dcc.Loading(
                        type="circle",
                        children=[
                            messages_div,
                            empty_page,
                            dbc.Row(
                                children=dbc.Col(
                                    children=[
                                        html.H2("report_title")
                                    ]
                                )
                            ),
                            *build_report_form(),
                            dbc.Row(
                                children=dbc.Col(
                                    children=[
                                        dbc.InputGroup(
                                            children=[
                                                dbc.Input(
                                                    id="new-tab-title",
                                                    type="text",
                                                    className="spark-input--sm",
                                                    placeholder="Enter new tab title",
                                                ),
                                                dbc.Button(
                                                    'Add Tab',
                                                    id='add-tab-btn',
                                                    className="spark-btn spark-btn--sm spark-btn"
                                                )
                                            ]
                                        )

                                    ],
                                    className="centered",
                                    width=4
                                ),
                                className="spark-mar-1 centered",
                                id="add-tab-btn-div",
                                style={"display": "none"},
                            ),

                            dbc.Container(
                                id="report-content-container",
                                children=[
                                    dbc.Row(
                                        children=dbc.Col(
                                            children=html.Div(
                                                id='tabs-container',
                                                children=["NO TABS CONTENT YET."]
                                            )
                                        )
                                    )]
                            ),
                            html.Br(),
                            dbc.Row(id="debug-content", className="debug-info-box"),
                        ]
                        ,
                        delay_show=100,
                        delay_hide=100,
                        overlay_style={"visibility": "visible", "filter": "blur(2px)"},

                    )
                )
            ),

            dcc.Location(id='url', refresh=True),
            *get_store(report_config)

        ],
        fluid=True,

    )

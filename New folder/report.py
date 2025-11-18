import logging
import time
import traceback
from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, State
from dash.html import Div, H3
from dash_bootstrap_components import Alert, Container, Row, Col
from fastapi import HTTPException

from app.core.config import settings
from custom_exceptions import NotFoundException
from dashboards.pages import read_cookie, read_configuration
from reports_index import report_class_index
from schemas.components.buttons import Button, debug_button, show_chart_settings_button
from schemas.components.header import Header
from schemas.components.scroll_to_top import scroll_to_top
from schemas.data_sources.data_sources_handler import DataSourceHandler
from schemas.report_context import ReportContext

logger = logging.getLogger(__name__)


# @callback(
#     Output("configuration_id_store", "data"),
#     Output("debug_store", "data"),
#     Output("date_end_store", "data"),
#     Output("date_start_store", "data"),
#     Output("template_store", "data"),
#     Input("url", "search"),
#     Input("debug-btn", "n_clicks"),
#     State("debug_store", "data"),
#
# )
# def url_into_store(search, debug_btn_clicks, current_debug_state):
#     configuration_id, debug, date_end, date_start, template = None, False, None, None, None
#
#     if search is not None:
#         search = unquote(search)
#         query_params = parse_qs(search.lstrip("?"))
#
#         configuration_id = query_params.get("configuration_id", [None])[0]
#         debug = query_params.get("debug", [False])[0]
#         date_end = query_params.get("date_end", [None])[0]
#         date_start = query_params.get("date_start", [None])[0]
#         template = query_params.get("template", [None])[0]
#
#     if debug_btn_clicks:
#         debug = not current_debug_state
#
#     return configuration_id, debug, date_end, date_start, template


#
# @callback(
#     Output("debug-content", "style"),
#     Output({"type": "component-debug", "index": ALL}, "style"),
#     Input("debug_store", "data"),
#     Input({"type": "component-debug", "index": ALL}, "value"),
#     prevent_initial_call=False
# )
# def toggle_debug_visibility(debug, component_debug_list):
#     debug_div_style = {"display": "block"} if debug in [True, "true"] else {"display": "none"}
#     return debug_div_style, [debug_div_style for _ in component_debug_list]
#

# Callback to handle the download button click
@callback(
    Output("download-pdf-btn", "href"),
    Input("download-pdf-btn", "n_clicks"),
    Input("url", "search"),
    Input("url", "href"),
)
def download_pdf(n_clicks, search, href):
    return href.replace("dash", "dash/pdf")


@callback(
    Output("send-to-gcs-pdf-btn", "href"),
    Input("send-to-gcs-pdf-btn", "n_clicks"),
    Input("url", "search"),
    Input("url", "href"),
)
def download_pdf(n_clicks, search, href):
    return href.replace("dash", "dash/pdf/to-gcs")


@callback(
    Output("see-configuration-btn", "href"),
    Input("see-configuration-btn", "n_clicks"),
    State("url", "search"),
    Input("url", "href"),
)
def download_pdf(n_clicks, search, href):
    base_url = "https://ocean.sabre.com/ocean-reports/"
    # Extract configuration id from url
    query_params = parse_qs(search.lstrip("?"))
    configuration_id = query_params.get("configuration_id", [None])[0]
    if configuration_id is None:
        return href
    if configuration_id.startswith("vbp"):
        href = f"{base_url}vbp-report?id={configuration_id}"
    elif configuration_id.startswith("kpi"):
        href = f"{base_url}kpi-report?id={configuration_id}"

    return href


# @callback(
#     Output({'type': 'chart-settings-div', 'index': MATCH}, 'is_open'),
#     Input({'type': 'chart-settings-btn', 'index': MATCH}, 'n_clicks'),
#     prevent_initial_call=True
# )
# def toggle_settings(n_clicks):
#     return n_clicks % 2 != 0

#
# @callback(
#     Output("charts_style_store", "data"),
#     Input({"type": "axis-1-auto-range", "index": ALL}, "value"),
#     Input({"type": "axis-1-range-mode", "index": ALL}, "value"),
#     Input({"type": "axis-1-show-ticks", "index": ALL}, "value"),
#     Input({"type": "axis-1-show-title", "index": ALL}, "value"),
#     Input({"type": "axis-2-auto-range", "index": ALL}, "value"),
#     Input({"type": "axis-2-range-mode", "index": ALL}, "value"),
#     Input({"type": "axis-2-show-ticks", "index": ALL}, "value"),
#     Input({"type": "axis-2-show-title", "index": ALL}, "value"),
#     State("charts_style_store", "data"),
#     State("template_id_store", "data"),
#     State({'type': 'chart-switchable', 'index': ALL}, 'figure'),
#     prevent_initial_call=True
# )
# def update_chart_styles_store(
#         axis_1_auto_range,
#         axis_1_range_mode,
#         axis_1_show_ticks,
#         axis_1_show_title,
#         axis_2_auto_range,
#         axis_2_range_mode,
#         axis_2_show_ticks,
#         axis_2_show_title,
#         store,
#         template_id,
#         figures
# ):
#     # Initialize template_id entry in store if not present
#     template_data = store.setdefault(
#         template_id, {
#             "axis_1_auto_range": [],
#             "axis_1_range_mode": [],
#             "axis_1_show_ticks": [],
#             "axis_1_title": [],
#             "axis_1_show_title": [],
#             "axis_2_auto_range": [],
#             "axis_2_range_mode": [],
#             "axis_2_show_ticks": [],
#             "axis_2_show_title": [],
#             "axis_2_title": [],
#
#         }
#     )
#
#     template_data["axis_1_auto_range"] = axis_1_auto_range
#     template_data["axis_1_range_mode"] = axis_1_range_mode
#     template_data["axis_1_show_ticks"] = axis_1_show_ticks
#     template_data["axis_1_show_title"] = axis_1_show_title
#     template_data["axis_2_auto_range"] = axis_2_auto_range
#     template_data["axis_2_range_mode"] = axis_2_range_mode
#     template_data["axis_2_show_ticks"] = axis_2_show_ticks
#     template_data["axis_2_show_title"] = axis_2_show_title
#
#     if len(template_data["axis_1_title"]) == 0:
#         template_data["axis_1_title"] = [figure["layout"]["yaxis"].get("title", "") for figure in figures]
#     if len(template_data["axis_2_title"]) == 0:
#         template_data["axis_2_title"] = [figure["layout"]["yaxis2"].get("title", "") for figure in figures]
#     return store


# @callback(
#     Output({"type": "chart-switchable", "index": ALL}, "figure"),
#     Input({"type": "chart-switchable", "index": ALL}, "figure"),
#     Input("charts_style_store", "data"),
#     State("template_id_store", "data"),
#     prevent_initial_call=True,
# )
# def read_charts_styles_store(figures, store, template_id):
#     if template_id in store:
#         template_data = store[template_id]
#
#         axis_1_auto_range_list = template_data.get("axis_1_auto_range", [])
#         axis_1_range_mode_list = template_data.get("axis_1_range_mode", [])
#         axis_1_show_ticks_list = template_data.get("axis_1_show_ticks", [])
#         axis_1_show_title_list = template_data.get("axis_1_show_title", [])
#         axis_1_title_list = template_data.setdefault("axis_1_title", [])
#         axis_2_auto_range_list = template_data.get("axis_2_auto_range", [])
#         axis_2_range_mode_list = template_data.get("axis_2_range_mode", [])
#         axis_2_show_ticks_list = template_data.get("axis_2_show_ticks", [])
#         axis_2_show_title_list = template_data.get("axis_2_show_title", [])
#         axis_2_title_list = template_data.setdefault("axis_2_title", [])
#
#         if len(axis_1_title_list) < len(figures):
#             axis_1_title_list.extend([""] * (len(figures) - len(axis_1_title_list)))
#         if len(axis_2_title_list) < len(figures):
#             axis_2_title_list.extend([""] * (len(figures) - len(axis_2_title_list)))
#
#         for e, (
#                 figure,
#                 axis_1_auto_range,
#                 axis_1_range_mode,
#                 axis_1_show_ticks,
#                 axis_1_show_title,
#                 axis_1_title,
#                 axis_2_auto_range,
#                 axis_2_range_mode,
#                 axis_2_show_ticks,
#                 axis_2_show_title,
#                 axis_2_title
#         ) in enumerate(
#             zip(
#                 figures,
#                 axis_1_auto_range_list,
#                 axis_1_range_mode_list,
#                 axis_1_show_ticks_list,
#                 axis_1_show_title_list,
#                 axis_1_title_list,
#                 axis_2_auto_range_list,
#                 axis_2_range_mode_list,
#                 axis_2_show_ticks_list,
#                 axis_2_show_title_list,
#                 axis_2_title_list,
#
#             )
#         ):
#
#             figure["layout"]["yaxis"]["autorange"] = bool(axis_1_auto_range)
#             figure["layout"]["yaxis"]["rangemode"] = axis_1_range_mode
#             figure["layout"]["yaxis"]["range"] = None if axis_1_auto_range else [0, 1]
#             figure["layout"]["yaxis"]["showticks"] = bool(axis_1_show_ticks)
#             figure["layout"]["yaxis"]["showtitle"] = bool(axis_1_show_title)
#
#             figure["layout"]["yaxis2"]["autorange"] = bool(axis_2_auto_range)
#             figure["layout"]["yaxis2"]["rangemode"] = axis_2_range_mode
#             figure["layout"]["yaxis"]["range"] = None if axis_1_auto_range else [0, 1]
#             figure["layout"]["yaxis2"]["showticks"] = bool(axis_2_show_ticks)
#             figure["layout"]["yaxis2"]["showtitle"] = bool(axis_2_show_title)
#
#             if axis_1_show_title:
#                 figure["layout"]["yaxis"]["title"] = axis_1_title
#             else:
#                 figure["layout"]["yaxis"]["title"] = ""
#             if axis_2_show_title:
#                 figure["layout"]["yaxis2"]["title"] = axis_2_title
#             else:
#                 figure["layout"]["yaxis2"]["title"] = ""
#     return figures


@callback(
    Output("configuration-id", "value"),
    Output("date-end", "value"),
    Output("date-start", "value"),
    Input("configuration_id_store", "data"),
    Input("date_end_store", "data"),
    Input("date_start_store", "data")
)
def load_store_to_form(configuration_id, date_end, date_start, ):
    return configuration_id, date_end, date_start


#
# @callback(
#     Output({'type': 'chart-table-div', 'index': MATCH}, 'is_open'),
#     Input({'type': 'chart-table-btn', 'index': MATCH}, 'n_clicks'),
#     prevent_initial_call=True
# )
# def toggle_chart_table_div(n_clicks):
#     return n_clicks % 2 != 0


# toggle_button = html.Button(
#     "Show/Hide Form",
#     id="toggle-form-btn",
#     className="spark-btn spark-btn--sm spark-btn-group-primary",
#     n_clicks=0,
# )

send_to_gcs_button = Button(
    uid="send-to-gcs-pdf-btn",
    href="",
    icon_class="spark-icon--fill spark-icon-file-upload spark-icon--md",
    tooltip="Upload PDF to GCS",
    target="_blank",
    n_clicks=0
).as_dash()


@callback(
    Output("report-content", "children"),
    Input("url", "search"),
    Input("url", "href"),

    prevent_initial_call=True
)
def build_report_content(search, href):
    kwargs = {}
    report_type = href.split("/")[-1].split("?")[0]

    query_params = parse_qs(search.lstrip("?"))
    configuration_id = query_params.get("configuration_id", [None])[0]

    report_class = report_class_index.get(
        report_type,
        None
    )
    debug_div = Row(id="debug-content", className="debug-info-box")

    if report_class.requires_configuration_id and configuration_id is None:
        dialog_is_open = True
        debug_content = "..."
        alert_content = []
        report_content = Div(
            [
                Alert(
                    children=[
                        Div(H3("No configuration selected."), className="alert-heading"),
                    ]
                )
            ]
        )
    else:

        if report_class is None:
            alert_content = []
            report_content = html.Div(
                [
                    html.Div(
                        id="no-data-banner",
                        children="No data available, try different dates or configuration.",
                        style={
                            "display": "block",  # Change to "none" when data is available
                            "padding": "20px",
                            "backgroundColor": "#f8d7da",
                            "color": "#721c24",
                            "border": "1px solid #f5c6cb",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "fontSize": "18px",
                        },
                    ),
                ]
            )
            debug_content = html.Div(
                id="debug-content",
                children=["Report class is None, the configuration_id received is not valid"]
                , className="debug-info-box"
            )
        else:
            alert_content = []
            kwargs.update({
                "handler": DataSourceHandler(),
            })
            [
                kwargs.update({key: value[0]}) for key, value in query_params.items()
                # TODO: can be extended to join if we want to pass multiple values
            ]

            # report_context = kwargs.get("context", ReportContext())
            report_context = ReportContext()
            kwargs.update({"report_context": report_context})

            try:
                report = report_class(**kwargs)
                ts = time.perf_counter()
                report_content = report.as_dash(**kwargs)

                rt = time.perf_counter() - ts
                dialog_is_open = False  # todo:
                debug_content = Row(
                    id="debug-content",
                    className="spark-panel debug-info-box",
                    children=[
                                 html.H3("Debug"),
                                 html.P(f"Response Time: {rt}s"),
                                 *[html.Pre(sql, style={"white-space": "pre-wrap"}) for sql in report_context.sqls]

                             ]
                             + [
                                 html.Ul([
                                     html.Li(
                                         [
                                             html.Strong(f"{key}: "),
                                             html.Span(value)
                                         ]
                                     )
                                     for key, value in report_context.timer.items()
                                 ]

                                 )
                             ] + [
                                 html.Div(str(report_context.observations))
                             ],
                    style={"display": "none"}
                )

                cleaned_obs = report_context.observations
                for e, alert in enumerate(cleaned_obs or []):
                    alert_content.append(
                        dbc.Badge(
                            [
                                html.I(
                                    className="spark-message__icon spark-icon-alert-triangle spark-icon--fill",
                                    **{'aria-hidden': 'true'}
                                ),
                                alert["message"]

                            ],
                            id=f"badge-alert-{str(e)}",
                            color="white",
                            text_color="danger" if alert.get("need_to_worry", False) else "warning",
                            className="border me-1",
                        ))

                    alert_content.append(dbc.Tooltip(
                        alert.get("details", "No details available"),
                        target=f"badge-alert-{str(e)}",  # Target the ID of the badge
                        placement="top"  # Position of the tooltip
                    )
                    )
            except NotFoundException as exc:
                alert_content = []
                report_content = html.Div(
                    [
                        html.Div(
                            id="no-data-banner",
                            children="No data available, try different dates or configuration.",
                            style={
                                "display": "block",  # Change to "none" when data is available
                                "padding": "20px",
                                "backgroundColor": "#f8d7da",
                                "color": "#721c24",
                                "border": "1px solid #f5c6cb",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "fontSize": "18px",
                            },
                        ),
                    ]
                )
                debug_content = html.Div(
                    id="debug-content",
                    children=["Report class is None, the configuration_id received is not valid"])
            except Exception as exc:

                print(f'{exc=}')
    debug_div.children = debug_content
    return Container(
        [
            html.Div(
                children=alert_content
            ),
            report_content,
            debug_div,
        ]
    )


def report_layout(_report_class, report_name="Ocean Reports", *args, **kwargs):
    try:
        admin_mode, user = read_cookie()
        user_is_external = "external" in user.roles
        read_configuration(configuration_id=kwargs.get("configuration_id"))
        server_is_external = settings.is_external()

        print(f"""
        LOADING...
        {args=}
        {kwargs=}
        {admin_mode=}
        {user=}
        {user_is_external=}
        {server_is_external=}
        {report_name=}
""")

    except HTTPException as exc:
        return Container(
            [
                Row(
                    [
                        Col
                            (
                            [
                                Alert(
                                    children=[
                                        Div(
                                            H3(f"{exc.detail}"),
                                            className="alert-heading"
                                        ),
                                    ],
                                    color="danger"
                                ),
                            ]
                        )]
                )]
        )
    except Exception as exc:
        return Container(
            Row(
                Col(
                    (
                        [
                            Alert(
                                children=[
                                    Div(H3(f"Error reading cookie: {exc}"), className="alert-heading"),
                                ], color="danger"
                            )
                        ]
                    )
                )
            )
        )
    include_nav = kwargs.get("include_nav", True)
    store = [
        dcc.Store(id="configuration_id_store", storage_type="session", data=None),
        dcc.Store(id="debug_store", storage_type="session", data=False),
        dcc.Store(id="date_end_store", storage_type="session", data=None),
        dcc.Store(id="date_start_store", storage_type="session", data=None),
        dcc.Store(id="template_store", storage_type="session", data=None),
        dcc.Store(id="chart_settings_store", storage_type="session", data=None),
        dcc.Store(id="charts_style_store", storage_type="session", data={}),
        dcc.Store(id="template_id_store", storage_type="session", data="vbp"),

    ]
    try:
        action_buttons = _report_class().action_buttons or []

        if admin_mode:
            action_buttons.extend(send_to_gcs_button)
            action_buttons.extend(show_chart_settings_button)
            action_buttons.extend(debug_button)

        navbar = Header(
            action_buttons=action_buttons,
            submit_form=_report_class().submit_form,
            dialog_is_open=False,
            title=report_name
        ).as_dash() if include_nav else ""
        return html.Div(
            children=scroll_to_top() + store + [
                dcc.Location(id="url", refresh=True),
                navbar,
                dcc.Loading(
                    html.Div(
                        id="report-content", children=[]
                    ),
                    delay_show=100,
                    delay_hide=100,
                    overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                    custom_spinner=html.Div(
                        html.H2(
                            [
                                "Loading Report  ",
                                dbc.Spinner(color="danger"),

                            ],
                            style={
                                "position": "fixed",
                                "top": "50%",
                                "left": "50%",
                                "transform": "translate(-50%, -50%)",
                                "z-index": "1000",
                                "color": "white",
                                "font-size": "3rem",
                                "background-color": "rgba(0, 0, 0, 0.5)",
                                "padding": "1rem",
                                "border-radius": "0.5rem",
                            }  # center it on the page
                        ),

                    )
                )

            ]
        )
    except Exception as exc:
        traceback.print_exc()
        logger.error(f"Error loading layout: {exc}")
        return Div(
            Alert(
                children=[
                    Div(H3(f"Error loading report: {exc}"), className="alert-heading"),
                ]
            ))

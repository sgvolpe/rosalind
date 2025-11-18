from typing import Optional, List, Any

import dash_bootstrap_components as dbc
from dash import html, dcc
from pydantic import BaseModel, Field

from schemas.components.dialog import Dialog


# from schemas.components.buttons import DownloadButton, UploadButton, ShowSettingsButton, OverflowDropdown
# from schemas.components.dialog import Dialog
# from schemas.kpi_report.submit_form import KpiSubmitForm

#
# @callback(
#     Output("kpi-report-spark-header-nav", "className"),
#     Output("close-menu", "n_clicks"),
#     [Input("navbar-toggler", "n_clicks")],
#     [Input("close-menu", "n_clicks")],
#     [State("navbar-collapse", "className")],
#     prevent_initial_call=True
#
# )
# def toggle_navbar_collapse(n, m, classname):
#     if m is None:
#         return "spark-header__nav", 0
#     if m == 1:
#         return "spark-header__nav", 0
#     if "active" not in classname:
#         return "spark-header__nav active", 0
#     else:
#         return "spark-header__nav", 0


# @callback(
#     Output('kpi-report-spark-header', 'className'),
#     Input('display', 'children'),
#     Input('kpi-report-spark-header', 'className'),
# )
# def update_window_size(breakpoint, classname):
#     if breakpoint == "xs":
#         classname = "spark-header spark-header--collapsed"
#     elif breakpoint == "sm":
#         classname = "spark-header spark-header--collapsed"
#     elif breakpoint == "md":
#         classname = 'spark-header spark-header--collapsed'
#     elif breakpoint == "lg":
#         classname = 'spark-header spark-header--overflow-checked spark-header--visible'
#     elif breakpoint == "xl":
#         classname = "spark-header spark-header--overflow-checked spark-header--visible"
#
#     else:
#         classname = "spark-header spark-header--visible spark-header--overflow-checked"
#
#     return classname

# #
# # @callback(
# #     Output("kpi-report-download-pdf", "href"),
# #     Input("url", "href")
# # )
# def update_download_button_href(href):
#     if href:
#         parsed_url = urlparse(href)
#         return f"/api/v1/data/kpi-report/pdf?{parsed_url.query}"


class Header(BaseModel):
    action_buttons: Optional[List] = Field(default=None)
    children: Optional[List] = Field(default_factory=list)
    dialog_is_open: Optional[bool] = Field(default=False)
    index: Optional[List] = Field(default=None)
    submit_form: Optional[Any] = Field(default=None)
    title: str = Field(default="Ocean Reports")
    uid: str = Field(default="kpi-report-spark-header-nav")

    def as_dash(self):
        resubmit_form_dialog = Dialog(
            modal=self.submit_form,
            title="Reload Report",
            className="",
            is_open=self.dialog_is_open
        ).as_dash() if self.submit_form is not None else None
        return html.Header(
            id="kpi-report-spark-header",
            className="spark-header spark-header spark-header--visible spark-header--overflow-checked",
            children=[
                dcc.Store(id='window-size-store', storage_type='session', data=[]),
                dbc.Nav(
                    id=self.uid,
                    className="spark-header__nav",
                    children=[
                        # dbc.Button(
                        #     id="navbar-toggler",
                        #     className="spark-menu__toggle spark-header__toggle ",
                        #
                        #     children=[
                        #         html.I(className="spark-icon--fill spark-icon-menu-hamburger spark-icon--md")
                        #     ],
                        # ),
                        html.Span(className="spark-header__logo", children=[
                            html.I(className="spark-logo spark-logo--sabre spark-logo--sm", children="Sabre")
                        ]),
                        html.A(href="#", className="spark-header__title", children=self.title),
                        html.Div(
                            className="spark-menu spark-header__menu",
                            role="menu",
                            children=[
                                html.Ul(
                                    className="spark-menu__list spark-header__list spark-header__list--overflow",
                                    children=[]
                                ),
                                html.Ul(
                                    className="spark-menu__list",
                                    children=[
                                                 html.Li(
                                                     className="spark-menu__list-item spark-menu__list-item--secondary",
                                                     children=resubmit_form_dialog
                                                 ),

                                             ] + [
                                                 html.Li(
                                                     className="spark-menu__list-item spark-header__more spark-no-animate",
                                                     children=el
                                                 )
                                                 for el in [self.action_buttons]
                                             ]
                                )
                            ]
                        )


                    ]
                )

            ],
            **{"data-breakpoint": "sm"}
        )

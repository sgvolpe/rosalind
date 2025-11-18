from typing import Optional, List

import dash_bootstrap_components as dbc
from dash import html, callback, Output, Input
from pydantic import BaseModel, Field


class DownloadButton(BaseModel):
    uid: str
    href: str
    children: list = None
    target: str = "_blank"
    tooltip: str = None

    def as_dash(self):
        children = self.children or [
            html.I(className="spark-icon--fill spark-icon-file-download spark-icon--md")
        ]
        download_button = html.A(
            id=self.uid,
            href=self.href,
            className="spark-header__title",
            children=children,
            target=self.target,

        )

        download_button_tooltip = dbc.Tooltip(
            self.tooltip,  # Text to show on hover
            target=self.uid,  # Target the button by its ID
            placement="top"  # Position of the tooltip (top, bottom, left, right)
        )
        return [download_button, download_button_tooltip]


class UploadButton(BaseModel):
    uid: str = "kpi-report-upload-button"
    href: str
    children: list = None
    target: str = "_blank"
    tooltip: str = "Upload the KPI report as a PDF to GCS"

    def as_dash(self):
        children = self.children or [
            html.I(className="spark-icon--fill spark-icon-file-upload spark-icon--md")
        ]
        upload_button = html.A(
            id=self.uid,
            href=self.href,
            className="spark-header__title",
            children=children,
            target=self.target,

        )

        upload_button_tooltip = dbc.Tooltip(
            self.tooltip,  # Text to show on hover
            target=self.uid,  # Target the button by its ID
            placement="top"  # Position of the tooltip (top, bottom, left, right)
        )
        return [upload_button, upload_button_tooltip]


@callback(
    Output("show_chart_settings-store", "data"),
    Input("show-chart-settings", "n_clicks"),
)
def show_chart_settings(n_clicks):
    return n_clicks or 0 % 2 or 0 != 0


class Button(BaseModel):
    uid: str
    href: Optional[str] = Field(default="#")
    children: list = None
    target: Optional[str] = "_blank"
    tooltip: str = None
    icon_class: str = None
    class_name: Optional[str] = Field(default="spark-header__title")
    n_clicks: int = 0

    def as_dash(self):
        children = self.children or [
            html.I(className=self.icon_class)
        ]
        if self.href is None and False:
            button = html.Button(
                id=self.uid,
                className="spark-header__title",
                n_clicks=self.n_clicks,
                children=children

            )
        else:
            button = html.A(
                id=self.uid,
                href=self.href,
                className="spark-header__title",
                children=children,
                target=self.target,
                n_clicks=self.n_clicks

            )

        button_tooltip = dbc.Tooltip(
            self.tooltip,  # Text to show on hover
            target=self.uid,  # Target the button by its ID
            placement="top"  # Position of the tooltip (top, bottom, left, right)
        )
        return [button, button_tooltip]


# class ShowSettingsButton(BaseModel):
#     uid: str = "show-chart-settings"
#     href: str = "#"
#     children: list = None
#     target: str = "_blank"
#     tooltip: str = "Show KPI report settings"
#
#     def as_dash(self):
#         children = self.children or [
#             html.I(
#                 className="spark-icon--fill spark-icon-cog spark-icon--md"
#             )
#         ]
#         show_settings_button = html.A(
#             id=self.uid,
#             href=f"#",
#             className="spark-header__title",
#             children=children
#         )
#
#         show_settings_tooltip = dbc.Tooltip(
#             "Show Chart Settings",  # Text to show on hover
#             target="show-chart-settings",  # Target the button by its ID
#             placement="top"  # Position of the tooltip (top, bottom, left, right)
#         )
#         return [show_settings_button, show_settings_tooltip]
#

class OverflowDropdown(BaseModel):
    uid: str
    children: list = None
    target: str = "_blank"
    tooltip: str = "Show more items"

    def as_dash(self):
        children = self.children or [
            html.I(className="spark-icon-menu-ellipsis-horizontal spark-icon--fill")
        ]
        overflow_dropdown = html.A(
            id=self.uid,
            className="spark-menu__list-link spark-menu__ignore",
            tabIndex=0,
            title=self.tooltip,
            children=children,

        )

        overflow_dropdown_tooltip = dbc.Tooltip(
            self.tooltip,  # Text to show on hover
            target=self.uid,  # Target the button by its ID
            placement="top"  # Position of the tooltip (top, bottom, left, right)
        )
        return [overflow_dropdown, overflow_dropdown_tooltip]


class OverFlowIcon(BaseModel):
    uid: str
    children: list = None
    target: str = "_blank"
    tooltip: str = "Show more items"

    def as_dash(self):
        children = self.children or [
            html.I(className="spark-icon-menu-ellipsis-horizontal spark-icon--fill")
        ]
        overflow_dropdown = html.A(
            id=self.uid,
            className="spark-menu__list-link spark-menu__ignore",
            tabIndex=0,
            title=self.tooltip,
            children=children,

        )

        overflow_dropdown_tooltip = dbc.Tooltip(
            self.tooltip,  # Text to show on hover
            target=self.uid,  # Target the button by its ID
            placement="top"  # Position of the tooltip (top, bottom, left, right)
        )
        return [overflow_dropdown, overflow_dropdown_tooltip]


class ContactUsButton(BaseModel):
    uid: str
    href: str = f"mailto:ocean.team@sabre.com"
    children: list = None
    target: str = "_blank"
    tooltip: str = "Contact Us"

    def as_dash(self):
        children = self.children or [
            html.I(className="spark-icon-mail spark-icon--fill spark-icon--md")
        ]
        contact_us_button = html.A(
            id=self.uid,
            href=self.href,
            className="spark-header__title",
            children=children,
            target=self.target,

        )

        contact_us_tooltip = dbc.Tooltip(
            self.tooltip,  # Text to show on hover
            target=self.uid,  # Target the button by its ID
            placement="top"  # Position of the tooltip (top, bottom, left, right)
        )
        return [contact_us_button, contact_us_tooltip]


see_configuration_button: List = Button(
    uid="see-configuration-btn",
    href="",
    icon_class="spark-icon--fill spark-icon-monitor-binary spark-icon--md",
    tooltip="See Configuration",
    target="_blank",
    n_clicks=0
).as_dash()

download_pdf_button: List = Button(
    uid="download-pdf-btn",
    href="",
    icon_class="spark-icon--fill spark-icon-file-download spark-icon--md",
    tooltip="Download PDF",
    target="_blank",
    n_clicks=0
).as_dash()

debug_button: List = Button(
    uid="debug-btn",
    href=None,
    tooltip="Debug",
    icon_class="",
    children=[html.Span("🦠")],
    n_clicks=0
).as_dash()

show_chart_settings_button = Button(
    uid="show-all-settings-btn",
    href=None,
    icon_class="spark-icon--fill spark-icon-cog spark-icon--md",
    tooltip="Show Chart settings",
    target="_blank",

    n_clicks=0
).as_dash()

edit_button: List = Button(  uid="edit-btn",
    href=None,
    tooltip="Edit/Save",
    icon_class="",
    children=["Edit"],
    n_clicks=0
).as_dash()

create_new_button: List = Button(
    uid="create-new-btn",
    href=None,
    tooltip="Create New",
    icon_class="",
    children=[html.Span("Create New")],
    n_clicks=0
).as_dash()

generate_pdf_button: List = Button(
    uid="generate-pdf-btn",
    href=None,
    tooltip="Generate PDF",
    icon_class="spark-icon--fill spark-icon-file-download spark-icon--md",

    children=[html.Span("Generate PDF")],
    n_clicks=0
).as_dash()

from typing import Optional, Any

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, Dash
from pydantic import BaseModel

from schemas.components.buttons import Button

app = Dash(__name__)


class Dialog(BaseModel):
    is_open: Optional[bool] = False
    modal: Optional[Any] = None
    title: Optional[str] = None
    uid: str = "kpi-dialog"

    def as_dash(self, *args, **kwargs):
        return Button(
            uid="open-form-btn",
            href="#",
            icon_class="spark-icon-arrows-update spark-icon--fill spark-icon--md",
            tooltip="Open Form",
            target=None,
            n_clicks=0
        ).as_dash() + [
                   dbc.Modal(
                       [
                           dbc.ModalHeader(dbc.ModalTitle(self.title)),
                           dbc.ModalBody(
                               dbc.Form(
                                   self.modal,
                                   className="",
                                   style={
                                       "padding": "3rem"
                                   },
                               ), style={
                                   "padding": "3rem"
                               },
                           ),
                           # dbc.ModalFooter(
                           #     dbc.Button("Close", id="close-form-btn", color="secondary", n_clicks=0)
                           # ),
                       ],
                       id="form-modal",
                       # className="spark-panel__content",
                       is_open=self.is_open,
                       style={
                           "zIndex": 10000,
                           # "width": "90%",
                           # "maxWidth": "600px", "margin": "auto",
                           "padding": "3rem"
                       },
                       size="xl"
                   )
               ]

    # # Callbacks for showing and hiding the modal
    @callback(
        Output("form-modal", "is_open"),
        State("form-modal", "is_open"),
        Input("open-form-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_modal(is_open, n_clicks):
        return not is_open

    @callback(
        Output("open-form-btn", "n_clicks"),
        Input("submit-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_button_counts(_):
        # Reset the button click counts to allow reopening the modal
        return 0

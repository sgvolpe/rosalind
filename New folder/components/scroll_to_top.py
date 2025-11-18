from typing import List

import dash_bootstrap_components as dbc
from dash import clientside_callback, dcc
from dash import html, Input, Output

clientside_callback(
    """
    function(n_intervals) {
        // Show button when scrolled down 100px from the top
        if (window.scrollY > 100) {
            document.getElementById("back-to-top").style.display = "block";
        } else {
            document.getElementById("back-to-top").style.display = "none";
        }
        return "";
    }
    """,
    Output("scroll-check-interval", "n_intervals"),  # Dummy output just to trigger the callback
    Input("scroll-check-interval", "n_intervals")  # Trigger every interval
)

# Callback to scroll back to the top when the button is clicked
clientside_callback(
    """
    function(n_clicks) {    
        window.scrollTo({ top: 0, behavior: "smooth" });
        return 1;
    }
    """,
    Output("back-to-top", "n_clicks"),
    Input("back-to-top", "n_clicks"),
    prevent_initial_call=True
)


def scroll_to_top() -> List[html.Div]:
    return [
        html.Div(id="scroll-output", style={"display": "none"}),
        dcc.Interval(id="scroll-check-interval", interval=250, n_intervals=0),  # Check every 500ms
        html.Button(
            id="back-to-top",
            className="spark-scroll-to-top visible",
            children=[
                html.I(
                    className="spark-scroll-to-top__icon"
                )]
            ,
        )
    ]


def get_floating_menu():
    return [html.Div(
        [
            # Main FAB Button
            dbc.Button(
                "+", id="fab-button", n_clicks=0, className="fab-button", color="primary", size="lg"
            ),
            # Additional Buttons (Menu Items)
            dbc.Button("Option 1", id="fab-option-1", className="fab-option", color="secondary"),
            dbc.Button("Option 2", id="fab-option-2", className="fab-option", color="secondary"),
            dbc.Button("Option 3", id="fab-option-3", className="fab-option", color="secondary"),
        ],
        id="fab-menu",
        style={"position": "fixed", "bottom": "30px", "right": "30px"}  # Positioning the FAB menu
    )]

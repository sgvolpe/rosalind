import dash_bootstrap_components as dbc
from dash import html
from pydantic import BaseModel, Field


class ChartControlBar(BaseModel):
    idx: int = Field(default=None)

    def as_dash(self, *args, **kwargs):
        return html.Div(
            id={"type": "chart-control-bar", "index": self.idx},
            children=[
                dbc.Button(
                    children=html.I(className="spark-icon--fill spark-icon-cog"),
                    className="mb-2",
                    color="dark",
                    id={"type": "chart-settings-btn", "index": self.idx},
                    n_clicks=0,
                    outline=True,
                    style={"display": "none"},

                ),
                dbc.Collapse(
                    is_open=False,
                    id={'type': 'chart-settings-div', 'index': self.idx},
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Chart Axis Settings", className="card-title mb-4"),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H6("Axis 1", className="text-primary"),

                                                    dbc.Label("Auto Range"),
                                                    dbc.Checklist(
                                                        id={"type": "axis-1-auto-range", "index": self.idx},
                                                        options=[{"label": "Auto Range", "value": 1}],
                                                        value=[1],
                                                        switch=True,
                                                        className="mb-3",
                                                    ),

                                                    dbc.Label("Range Mode"),
                                                    dbc.Select(
                                                        id={"type": "axis-1-range-mode", "index": self.idx},
                                                        options=[
                                                            {"label": "Normal", "value": "normal"},
                                                            {"label": "To Zero", "value": "tozero"},
                                                            {"label": "Non Negative", "value": "nonnegative"},
                                                        ],
                                                        className="mb-3",
                                                    ),

                                                    dbc.Label("Show Axis Ticks"),
                                                    dbc.Checklist(
                                                        id={'type': "axis-1-show-ticks", "index": self.idx},
                                                        options=[{"label": "Show Axis Ticks", "value": 1}],
                                                        value=[1],
                                                        switch=True,
                                                        className="mb-3",
                                                    ),

                                                    dbc.Label("Show Axis Title"),
                                                    dbc.Checklist(
                                                        id={"type": "axis-1-show-title", "index": self.idx},
                                                        options=[{"label": "Show Axis 1 Title", "value": 1}],
                                                        value=[1],
                                                        switch=True,
                                                        className="mb-3",
                                                    ),
                                                ]
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H6("Axis 2", className="text-primary"),

                                                    dbc.Label("Auto Range"),
                                                    dbc.Checklist(
                                                        id={"type": "axis-2-auto-range", "index": self.idx},
                                                        options=[{"label": "Auto Range", "value": 1}],
                                                        value=[1],
                                                        switch=True,
                                                        className="mb-3",
                                                    ),

                                                    dbc.Label("Range Mode"),
                                                    dbc.Select(
                                                        id={"type": "axis-2-range-mode", "index": self.idx},
                                                        options=[
                                                            {"label": "Normal", "value": "normal"},
                                                            {"label": "To Zero", "value": "tozero"},
                                                            {"label": "Non Negative", "value": "nonnegative"},
                                                        ],
                                                        className="mb-3",
                                                    ),

                                                    dbc.Label("Show Axis Ticks"),
                                                    dbc.Checklist(
                                                        id={'type': "axis-2-show-ticks", "index": self.idx},
                                                        options=[{"label": "Show Axis Ticks", "value": 1}],
                                                        value=[1],
                                                        switch=True,
                                                        className="mb-3",
                                                    ),

                                                    dbc.Label("Show Axis Title"),
                                                    dbc.Checklist(
                                                        id={"type": "axis-2-show-title", "index": self.idx},
                                                        options=[{"label": "Show Axis 2 Title", "value": 1}],
                                                        value=[1],
                                                        switch=True,
                                                        className="mb-3",
                                                    ),
                                                ]
                                            ),
                                        ]
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )

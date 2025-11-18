import logging

from dash import dcc
from dash import html
from pydantic import Field, BaseModel

logger = logging.getLogger(__name__)


class TabControlBar(BaseModel):
    idx: int = Field(default=None)

    def as_dash(self, *args, **kwargs):
        return html.Div(
            id={"type": "tab-control-bar", "index": self.idx},
            children=[
                html.H4(f"tabControlBar: {self.idx}"),
                dcc.Input(
                    id={"type": "tab-control-bar-input", "index": self.idx},
                    type="text",
                    value="",
                    placeholder="Enter a value...",
                ),
                html.Div(
                    [
                        html.H4(f"Dropdown Tables: {self.idx}"),
                        dcc.Dropdown(
                            id={"type": "tab-control-bar-dropdown-tables", "index": self.idx},
                            options=[{'label': k, 'value': k} for k, v in
                                     components_index.get('dropdown_tables', {}).items()],
                            value=None
                        ),
                    ]
                ),
            ]
        )

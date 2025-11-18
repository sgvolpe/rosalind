import base64
from enum import Enum
from typing import Optional, List, Union, Tuple, Dict, ClassVar, Callable

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from dash import dcc, html, dash_table
from pydantic import Field, BaseModel

from schemas.custom_report import ComponentBase, H2Component
from schemas.custom_report.chart_control_bar import ChartControlBar

MAIN_PALETTE = [
    "#5a82ad",  # Blue
    "#F28E2B",  # Orange
    "#E15759",  # Red
    "#76B7B2",  # Teal
    "#59A14F",  # Green
    "#EDC949",  # Yellow
    "#AF7AA1",  # Purple
    "#FF9DA7",  # Pink
    "#9C755F",  # Brown
    "#BAB0AC",  # Gray
]
CONTRAST_PALETTE = [
    "#1F77B4",  # Darker Blue
    "#FF7F0E",  # Brighter Orange
    "#D62728",  # Strong Red
    "#2CA02C",  # Bold Green
    "#9467BD",  # Deep Purple
    "#8C564B",  # Dark Brown
    "#E377C2",  # Vivid Pink
    "#7F7F7F",  # Dark Gray
    "#BCBD22",  # Lime Green
    "#17BECF",  # Cyan
]

# colors_index = {
#     "avg_response_time": "#1f77b4",
#     "empty_responses": "#d06b6b",
#     "empty_responses_percent": "#101056",
#     "failure_rate": "#e7cc00",
#     "l2b": "#00e7cc",
#     "number_of_sessions_with_success": "#4BF3A0",
#     "requests": "#00e7cc",
#     "sell_sessions_with_failure": "#f35a4b",
#
# }
colors_index = {
    "average_number_of_itineraries": MAIN_PALETTE[5],
    "avg_response_time": MAIN_PALETTE[4],
    "bookings": MAIN_PALETTE[1],
    "empty_responses": MAIN_PALETTE[2],
    "empty_responses_percent": MAIN_PALETTE[3],
    "failure_rate": "#ffbe7d",
    "l2b": CONTRAST_PALETTE[1],
    "number_of_sessions_with_success": "#c4dfd8",
    "requests": MAIN_PALETTE[6],
    "l2b_rq": MAIN_PALETTE[0],
    "sell_sessions_with_failure": "#f15854",

}

class ChartTraceType(str, Enum):
    AREA = "area"
    BAR = "bar"
    HBAR = "hbar"
    HISTOGRAM = "histogram"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"


class ChartTrace(BaseModel):
    """
    Represents a trace in a chart, which is a single series of data points.

    Attributes:
        color (Optional[str]): The color of the trace.
        custom_text (Optional[Union[str, List, dict]]): Custom text to display on the trace. If str, it will be displayed as passed.
        if dict, it should have a column key and a format key. The column key is the column in the dataframe to use for the text, and
        format a callable to apply to the column.
        line_width (Optional[float]): The width of the line in the trace.
        mode (Optional[str]): The mode of the trace, e.g., 'lines+markers'.
        name (Optional[str]): The name of the trace.
        opacity (Optional[float]): The opacity of the trace.
        secondary (bool): Whether the trace is secondary.
        show_text (Optional[bool]): Whether to show text on the trace.
        text_format (Optional[Callable]): The format of the text.
        text_position (Optional[str]): The position of the text, if the trace is a bar.
        type (ChartTraceType): The type of the trace.
        x (Optional[str]): The x-axis data for the trace.
        y (Optional[str]): The y-axis data for the trace.
    """
    color: Optional[str] = Field(default=None)
    custom_text: Optional[Union[str, List, dict]] = Field(default=None)
    line_width: Optional[float] = Field(default=2)
    line_dash: Optional[str] = Field(default="solid")  # "solid, dot, dash, longdash, dashdot, longdash dot
    mode: Optional[str] = Field(default="lines+markers")
    name: Optional[str] = Field(default=None)
    opacity: Optional[float] = Field(default=1)
    secondary: bool = Field(default=False)
    show_text: Optional[bool] = Field(default=False)
    text_format: Optional[Callable] = Field(default=str)
    text_position: Optional[str] = Field(default=None)  # If bar ['inside', 'outside', 'auto', 'none']
    type: ChartTraceType = Field(default=None)
    x: Optional[str] = Field(default=None)
    y: Optional[str] = Field(default=None)

    def as_json(self, *args, **kwargs):
        """This method is to account for the different parameters a trace can have
        based on the trace type
        """

        if self.color is None:
            self.color = colors_index.get(self.y, None)

        trace_args = {
            "name": self.name,
            "opacity": self.opacity,
            "textposition": self.text_position or "top center",
            "yaxis": "y2" if self.secondary else "y",
        }

        if self.type.value == "line":
            if kwargs.get("printable", False):
                col_x = kwargs.get("col_x", 12)
                line_width = self.line_width * 12 / col_x
            else:
                line_width = self.line_width
            trace_args.update(
                {
                    "line": {"color": self.color, "width": line_width, "dash": self.line_dash},
                    "mode": self.mode,
                    "opacity": self.opacity,
                    "textposition": self.text_position or "top center",
                }
            )
        elif self.type.value == "bar":
            trace_args.update(
                {
                    "marker": {"color": self.color},
                    "textposition": self.text_position or "auto",

                }
            )
        elif self.type.value == "hbar":
            trace_args.update(
                {
                    "marker": {"color": self.color},
                    "textposition": self.text_position or "auto",
                    "orientation": "h"

                }
            )
        elif self.type.value == "area":

            if kwargs.get("printable", False):
                col_x = kwargs.get("col_x", 12)
                line_width = self.line_width * 12 / col_x
            else:
                line_width = self.line_width

            trace_args.update(
                {
                    "fill": "tozeroy",
                    "fillcolor": self.color,  # 'rgba(0, 0, 255, 0.3)',
                    "line": {"color": self.color, "width": line_width},
                    "mode": self.mode,
                    "textposition": "middle right",
                }

            )
        return trace_args


class ChartHorizontalLine(BaseModel):
    color: Optional[str] = Field(default="#bb8b16")
    dash: Optional[str] = Field(default="dash")
    method: Optional[Callable] = Field(default=None)
    mode: Optional[str] = Field(default="lines")
    name: Optional[str] = Field(default=None)
    secondary_axis: bool = Field(default=False)
    value: Optional[Union[float, str]]

    def as_dash(self, df, *args, **kwargs):
        if self.value is None and self.method is not None:
            self.value = self.method(df, *args, **kwargs)
        line_trace = go.Scatter(
            x=[df.index.min(), df.index.max()],
            y=[self.value] * len(df),
            mode=self.mode,
            line=dict(dash=self.dash, color=self.color),
            name=self.name,
            yaxis="y2" if self.secondary_axis else "y1"  # Specify the secondary y-axis
        )
        return line_trace

    def as_shape(self, df, *args, **kwargs) -> Tuple[Dict, Dict]:
        if self.value is None and self.method is not None:
            self.value = self.method(df, *args, **kwargs)

        if int(self.value) > 0:
            line_shape = {
                "line": {"color": self.color, "dash": self.dash, "width": 2},
                "type": "line",
                "x0": 0, "x1": 1,
                "xref": "paper",
                "y0": self.value, "y1": self.value,
                "yref": "y2" if self.secondary_axis else "y",
            }

            annotation = {
                "bgcolor": "white",
                "bordercolor": self.color,
                "borderwidth": 1,
                "font": {"color": self.color, "size": 12},
                "showarrow": False,
                "text": f"Target {int(self.value)}",
                "x": 0.9,  # Right side of the chart (paper coordinate)
                "xanchor": "left",  # Align left to prevent overlap
                "xref": "paper",
                "y": f"{self.value}",
                "yref": "y2" if self.secondary_axis else "y",
            }
            return line_shape, annotation

        else:
            return None, None


class ChartComponent(ComponentBase):
    bar_mode: str = Field(default=None)
    bar_corner_radius: float = Field(default=5)
    bar_gap: float = Field(default=0.02)
    bar_group_gap: float = Field(default=0.03)
    class_name: str = Field(default="spark-panel__content spark-chart")
    description: str = Field(default=None)
    df: pd.DataFrame = Field(default=None)
    height: Optional[int] = Field(default=400)
    hover_mode: Optional[str] = Field(default="x unified")  # "x" | "y" | "closest" | False | "x unified" | "y unified"
    horizontal_line: Optional[ChartHorizontalLine] = Field(default=None)
    index: Optional[str] = Field(default=None)
    include_chart_control_bar: Optional[bool] = Field(default=True)
    include_data_table_div: Optional[bool] = Field(default=True)
    include_footer: Optional[bool] = Field(default=False)
    instance_count: ClassVar[int] = 0
    layout: Dict = Field(default_factory=dict)
    legend: Dict = Field(default=None)
    max_width_of_bar: Optional[float] = Field(default=0.5)
    show_legend: bool = Field(default=True)
    style: Optional[str] = Field(default="width:100%;height:100%")
    template: Optional[str] = Field(default="plotly_white",
                                    description="""['ggplot2', 'seaborn', 'simple_white', 'plotly','plotly_white', 
                                    'plotly_dark', 'presentation', 'xgridoff','ygridoff', 'gridon', 'none']
                                    """)
    title: str = Field(default=None)
    traces: List[ChartTrace] = Field(default_factory=list)
    type: str = Field(default="line")
    width: Optional[int] = Field(default=1000)
    x_axis: Optional[dict] = Field(default=None)
    x_column: str = Field(default=None)
    y_axis1: Optional[dict] = Field(default=None)
    y_axis2: Optional[dict] = Field(default=None)
    model_config = {
        "arbitrary_types_allowed": True
    }

    def as_dash(self, *args, **kwargs) -> List:
        ChartComponent.instance_count += 1
        if self.df is None and self.method is not None:
            self.df = self.method(*args, **kwargs)

        fig = go.Figure()

        # Add horizontal line if specified
        if self.horizontal_line is not None:
            line_shape, annotation = self.horizontal_line.as_shape(df=self.df, *args, **kwargs)
        else:
            line_shape, annotation = None, None

        # Determine font size based on printable flag
        if kwargs.get("printable", False):
            col_x = kwargs.get("col_x", 12)
            font_size = dict(size=12 * 12 / col_x)
        else:
            font_size = dict(size=10)

        # Add traces to the figure
        for trace in self.traces:
            fig.add_trace(
                getattr(go, trace.type.value.capitalize())(
                    x=self.df[trace.x] if trace.x else self.df.index,
                    y=self.df[trace.y] if trace.y else None,
                    **trace.as_json(*args, **kwargs)
                )
            )

        # Configure axes
        y_axis1 = {
            "showticklabels": True,
            "tickfont": font_size,
            "visible": True,
        }
        if self.y_axis1 is not None:
            y_axis1.update(self.y_axis1)

        y_axis2 = {
            "overlaying": "y",  # Share the same x-axis
            "showgrid": False,
            "showticklabels": True,
            "side": "right",  # Place secondary axis on the right
            "tickfont": font_size,
            "visible": True,
        }

        if self.y_axis2 is not None:
            y_axis2.update(self.y_axis2)
        x_axis = {
            "tickfont": font_size,
            "tickformat": "%b %d",
            "type": 'category'
        }

        if self.x_axis is not None:
            x_axis.update(self.x_axis)

        _legend = dict(
            x=0,  # Align to the left
            y=-0.2,  # Align to the bottom
            xanchor='left',  # Anchor point for x (can be 'left', 'center', 'right')
            yanchor='bottom',  # Anchor point for y (can be 'top', 'middle', 'bottom')
            orientation="h",
            font={"size": font_size.get("size") * 0.8}

        )
        fig.update_layout(
            # annotations=[annotation] if annotation is not None else None,
            autosize=True,
            bargap=self.bar_gap,  # Gap between bars within a group
            bargroupgap=self.bar_group_gap,  # Gap between groups of bars (if multiple traces exist)
            hovermode=self.hover_mode,
            barcornerradius=self.bar_corner_radius,
            barmode=self.bar_mode,
            legend=_legend if self.show_legend else None,
            margin=dict(b=1, l=1, r=1, t=1, ),
            shapes=[line_shape] if line_shape is not None else None,
            showlegend=self.show_legend,
            template=self.template or "plotly_white",
            xaxis=x_axis,
            xaxis_title=self.x_column,
            yaxis_title=self.traces[0].name,
            yaxis=y_axis1,
            yaxis2=y_axis2,

        )
        if self.include_chart_control_bar:
            chart_control_bar = ChartControlBar(
                idx=ChartComponent.instance_count
            ).as_dash(*args, **kwargs)
        else:
            chart_control_bar = None

        #
        if self.include_data_table_div:
            data_table_div = self.build_data_table(ChartComponent.instance_count, self.df.reset_index())
        else:
            data_table_div = None

        if self.include_footer:
            table_footer = html.Div(
                className="component-footer",
                children=[
                    html.Div(
                        className="component-footer-title",
                        children=(self.title or "") + " " + (self.uid or "")
                    ),
                    html.Div(
                        className="component-footer-content",
                        children=self.description
                    )
                ]
            )
        else:
            table_footer = None
        return [
            H2Component(children=self.title or "").as_dash(*args, **kwargs),

            dcc.Graph(
                config={
                    "displayModeBar": "hover",
                    "modeBarButtonsToRemove": [
                        "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d",
                        "resetScale2d", "hoverClosestCartesian", "hoverCompareCartesian", "toggleSpikelines"
                    ],
                    "displaylogo": False,
                },
                figure=fig,
                # id={"type": "chart-switchable", "index": idx},
                style={"width": "100%", "height": "100%"}
            ),
            chart_control_bar,
            data_table_div,
            table_footer,
        ]

    def as_html(self, *args, **kwargs):
        self.children = [*self.as_dash(*args, **kwargs)]
        try:
            kwargs.update({"printable": True})

            for element in self.children:
                if isinstance(element, dcc.Graph):
                    try:
                        base_64_str = base64.b64encode(
                            pio.to_image(
                                element.figure, format="png", width=self.width, height=self.height,
                                scale=float(kwargs.get("img_res", 1))
                            )
                        ).decode('utf-8')
                    except Exception as exc:
                        raise exc
                        base_64_str = ""

                    return f"""
                    {f'<h4 class="centered"> {self.title} </h4>' if self.title else ''}
                    <img src='data:image/png;base64,{base_64_str}' style="{self.style}", alt="[NO DATA]"/>
                    """
            else:
                raise ValueError("No chart found")
        except Exception as exc:
            print(f"Exception on chart as html: {exc=}")
            raise exc

    def build_data_table(self, idx, df):
        data_table_div = html.Div(
            id="data-table-div",
            children=[
                dbc.Button(
                    children=[
                        html.I(
                            className="spark-icon--fill spark-icon-design-ruler-corner"
                        ),
                    ],
                    className="mb-2",
                    color="dark",
                    id={"type": "chart-table-btn", "index": idx},
                    n_clicks=0,
                    outline=True,
                    style={"display": "none"}
                ),
                dbc.Collapse(
                    is_open=False,
                    id={'type': 'chart-table-div', 'index': idx},
                    children=[
                        html.Div(
                            id=f"chart-table-{idx}",
                            children=[
                                dash_table.DataTable(
                                    # id=table_id,
                                    columns=[{"name": col, "id": col} for col in df.columns],
                                    data=df.to_dict('records'),
                                    style_table={'overflowX': 'auto'},
                                    style_cell={
                                        'height': 'auto',
                                        'minWidth': '0px', 'maxWidth': '180px',
                                        'whiteSpace': 'normal'
                                    },
                                )
                            ]

                        )

                    ]

                )
            ]
        )
        return data_table_div

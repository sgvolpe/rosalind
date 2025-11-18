import colorsys
import logging
from typing import Callable, Optional, List, Union

import numpy as np
import pandas as pd
from dash import dash_table
from dash import html
from pydantic import Field, BaseModel

from helpers import human_readable
from schemas.components import table_formatting_methods
from schemas.components.error import catch_with_error_component_dash, catch_with_error_component_html
from schemas.components.ui_base_component import UIBaseComponent

logger = logging.getLogger(__name__)
numeric_align_table_style = {
    "if": {"column_id": "numeric_column"},
    "textAlign": "right",  # Right-align numeric columns
}


def color_for_bookability(x, col_name: str = None, *args, **kwargs):
    """
    Determines a color based on the bookability percentage.

    Args:
        x: The bookability value to evaluate.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        apply_factor (float, optional): A factor to apply to the thresholds. Defaults to 1.

    Returns:
        str: The determined color. If the value is less than 10% of the apply_factor, returns "green".
             If the value is 20% or more of the apply_factor, returns "red". Otherwise, returns "orange".
    """
    apply_factor = kwargs.get("apply_factor", 1)
    if float(str(x).split("%")[0]) < 0.1 * apply_factor:
        return "green"
    if float(str(x).split("%")[0]) >= 0.2 * apply_factor:
        return "red"
    else:
        return "orange"


def color_for_target(x, target: float = None, tolerance_percentage: float = None, tolerance: float = None,
                     col_name: str = None, *args, **kwargs):
    """
    Determines a color based on how a value compares to a target value within a specified tolerance.

    Args:
        x: The value to compare to the target.
        target (float): The target value.
        tolerance_percentage (float, optional): The tolerance as a percentage of the target. If provided, this is used to calculate the tolerance.
        tolerance (float, optional): The tolerance as an absolute value. If provided, this is used as the tolerance.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        str: The determined color. If the value is within the tolerance, returns "orange". If the value is less than the target minus the tolerance, returns "green". Otherwise, returns "red".

    Raises:
        ValueError: If neither tolerance_percentage nor tolerance is provided.
    """
    try:
        if isinstance(x, str):
            x = x.replace("%", "")
            x = str(x).split("\n")[0]
        x = float(x)
    except Exception as exc:
        logger.error(
            f"""
        Error occurred while converting {x} to float on color_for_target.
        {exc=}
        """
        )

        return "lightgrey"
    if target is None:
        return ""
    if tolerance_percentage is not None:
        top_limit = target * (1 + tolerance_percentage)
        bottom_limit = target * (1 - tolerance_percentage)
    elif tolerance is not None:
        top_limit = target + tolerance
        bottom_limit = target - tolerance
    else:
        raise ValueError("color_for_target: Either tolerance or tolerance_percentage must be provided")

    if x == np.inf or x == -np.inf or np.isnan(x):
        color = "grey"

    elif bottom_limit < x < top_limit:
        color = "orange"
    elif x <= target * (1 - tolerance_percentage):
        color = "green"
    else:
        context = kwargs.get("context")

        if context is not None:
            context.add_red_flags(
                [
                    {
                        col_name: f"Value {x} is above target {target} by {x - target}."
                    }
                ]
            )
        color = "red"

    return color

def lighten_color(hex_color, amount=0.8):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    l = min(1, l + amount * (1 - l))  # increase lightness
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

def get_color_for_val_in_range(val, min_val, max_val, base_color):
    range_span = max_val - min_val or 1
    ratio = (val - min_val) / range_span

    return  lighten_color(base_color, amount=1 - ratio)

def generate_gradient_styles(df, **column_colors):

    styles = []
    for column in df.columns:
        if column in column_colors: # pd.api.types.is_numeric_dtype(df[column]) and
            base_color = column_colors[column]
            col_min = df[column].min()
            col_max = df[column].max()
            range_span = col_max - col_min or 1

            for i, value in enumerate(df[column]):
                try:
                    if isinstance(value, str):
                        value = value.replace("%", "")
                        value = str(value).split("\n")[0]
                    value = float(value)
                except Exception as exc:
                    
                    print(f'{exc=}')

                ratio = (value - col_min) / range_span
                light_color = lighten_color(base_color, amount=1 - ratio)
                styles.append({
                    'if': {
                        'column_id': column,
                        'row_index': i
                    },
                    'backgroundColor': light_color,
                    'color': 'black'
                })
    return styles

def color_gradient(x, colorscale=["#D0E1F9", "#022E7A"], *args, **kwargs):
    """
    Applies a color gradient to a value based on its position in a range.

    Args:
        x: The value to color.
        colorscale (list): A list of two colors defining the gradient.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        str: The color for the value based on its position in the range.
    """
    try:
        if isinstance(x, str):
            x = x.replace("%", "")
            x = str(x).split("\n")[0]
        x = float(x)
    except Exception as exc:
        logger.error(
            f"""
        Error occurred while converting {x} to float on color_gradient.
        {exc=}
        """
        )
        return "lightgrey"

    if x == np.inf or x == -np.inf or np.isnan(x):
        return "grey"

    norm_value = (x - min(colorscale)) / (max(colorscale) - min(colorscale))  # Normalize 0 to 1
    color = f"rgba({int((1 - norm_value) * 255)}, {int((1 - norm_value) * 255)}, 255, 1)"  # Blue gradient

    return color

class TableColoring(BaseModel):
    method: Optional[Callable] = Field(default=None)
    target: Optional[float] = Field(default=2000)
    tolerance: Optional[float] = Field(default=None)
    tolerance_percentage: Optional[float] = Field(default=None)
    columns: Optional[List[str]] = Field(default_factory=list)


class Table(UIBaseComponent):

    ascending: Optional[bool] = Field(default=False)
    class_name: str = Field(default="spark-panel__content spark-table")
    col_limit: Optional[int] = Field(default=None)
    col_offset: Optional[int] = Field(default=None)
    coloring: Optional[TableColoring] = Field(default=None)
    column_formatting: Callable = Field(default=lambda x: x.replace("_", " ").title())
    columns: Optional[Union[List, Callable]] = Field(default=None, description="Columns to show in the table.")
    df: Optional[pd.DataFrame] = Field(default=None)
    filter_action: Optional[str] = Field(default="none")
    formatting_method: Optional[Callable] = Field(default=human_readable)
    header_method: Optional[Callable] = Field(default=None)
    include_footer: Optional[bool] = Field(default=False)
    page_action: Optional[str] = Field(default="none")
    page_size: Optional[int] = Field(default=10)
    row_limit: Optional[int] = Field(default=None)
    row_offset: Optional[int] = Field(default=None)
    sort_key: Optional[Union[str]] = Field(default=None)
    sort_mode: Optional[str] = Field(default="multi")
    sortable: Optional[str] = Field(default="none") # "native"
    style_header: Optional[dict] = Field(default=None)
    style_conditional: Optional[dict] = Field(default=None)
    title: Optional[str] = Field(default=None)
    model_config = {
        "arbitrary_types_allowed": True
    }

    @catch_with_error_component_dash
    def as_dash(self, *args, **kwargs) -> html.Div:
        logger.debug(f"""
        ====================================
                TABLE AS DASH
        ====================================
            - {self.title=}
            - {self.uid=}
            - {self.row_limit=}
            - {self.row_offset=}
            - {self.col_limit=}
            - {self.col_offset=}
            - {self.sort_key=}  
            - {self.ascending=}

        """)
        if self.method is not None:
            self.df = self.method(*args, **kwargs)
        self.limit_data()  # Limit Before formatting, so numbers don't get treated as str for sorting
        if self.style_conditional is None:
            style_conditional = self.get_style_data_conditional(*args, **kwargs)
        else:
            style_conditional_method = self.style_conditional.get("method")
            style_conditional_kwargs = self.style_conditional.get("kwargs", {})
            style_conditional = style_conditional_method(self.df, **style_conditional_kwargs)
        self.format_table(self.formatting_method)
        self.children = []
        table_footer = html.Div(
            className="component-footer",
            children=[
                html.Div(
                    className="component-footer-title",
                    children=self.title + " " + self.uid
                ),
                html.Div(
                    className="component-footer-content",
                    children=self.description
                )
            ]
        )

        _cols_to_show = self._columns_to_show()
        

        style_header = {
            "backgroundColor": "#f4f4f4",  # Light grey header background
            "fontWeight": "bold",  # Bold font for headers
            "textAlign": "center",  # Center-align header text
            "borderBottom": "2px solid #ccc",  # Add a subtle border
            # "textTransform": "capitalize",  # Title case for header text
            "fontSize": "14px",  # Standard font size
        }
        

        if self.style_header:
            style_header.update(self.style_header)
        if self.df.shape[0] == 0:
            _data = self.df.to_dict('records')
        elif self.df.empty:


            _data = {}
        else:
            _data = self.df.to_dict('records')
        

        return html.Div(
            className=self.class_name,
            children=[
                html.H2(self.title),
                dash_table.DataTable(
                    sort_action=self.sortable ,  # enables column sorting
                    filter_action=self.filter_action,  # enables filtering
                    page_action=self.page_action,  # enables pagination
                    page_size=self.page_size,  # default page size
                    sort_mode=self.sort_mode,  # default page size
                    id=self.uid,
                    style_data={
                        "height": "auto",  # Adjust row height for content
                        "padding": "10px",  # Add padding for cleaner appearance
                        # "whiteSpace": "normal",#
                        'whiteSpace': 'pre-line',
                        # 'height': 'auto',
                    },
                    style_header=style_header,
                    style_table={
                        "border": "1px solid #ccc",  # Light border around the table
                        "borderRadius": "5px",  # Rounded corners
                        "overflowX": "auto",  # Enable horizontal scrolling if needed
                        "width": "100%",
                    },
                    style_cell={
                        "backgroundColor": "white",  # Clean white background
                        "border": "1px solid #eee",  # Subtle cell borders
                        "color": "#333",  # Text color
                        "fontFamily": "Roboto, sans-serif",
                        # "fontSize": "14px",  # Standard font size
                        "textAlign": "center",
                        'overflow': 'hidden',
                        'whiteSpace': 'pre-line',  # Allows '\n' to create line breaks

                    },

                    columns=[
                        {
                            "name": self.column_formatting(col), "id": col
                        } for col in _cols_to_show
                    ] if self.column_formatting is not None else _cols_to_show,
                    css=[
                        {"selector": "table", "rule": "width: 100%; border-collapse: collapse;"},
                    ],
                    data=_data,
                    style_data_conditional=style_conditional
                ),
                table_footer if self.include_footer else None
            ]
        )

    def _columns_to_show(self):
        """
        Determines the columns to display in the table based on the `self.columns` attribute.

        Functionality:
        1. If `self.columns` is not `None`:
           - If `self.columns` is a list, it directly uses the list as the columns to show.
           - If `self.columns` is a callable, it iterates through the DataFrame's columns and includes only those for which the callable returns `True`.
        2. If `self.columns` is `None`, all columns from the DataFrame (`self.df.columns`) are included.

        Returns:
        - List: A list of column names to display.

        Instance Variables:
        - `self.columns`: Specifies the columns to show. Can be a list of column names or a callable.
        - `self.df`: The DataFrame whose columns are being processed.

        Example:
            # Case 1: `self.columns` is a list
            self.columns = ['A', 'B']
            _columns_to_show() -> ['A', 'B']

            # Case 2: `self.columns` is a callable
            self.columns = lambda col: col.startswith('A')
            self.df.columns = ['A1', 'A2', 'B1']
            _columns_to_show() -> ['A1', 'A2']

            # Case 3: `self.columns` is None
            self.df.columns = ['A', 'B', 'C']
            _columns_to_show() -> ['A', 'B', 'C']
        """
        _cols_to_show = []
        if self.columns is not None:
            if isinstance(self.columns, List):
                _cols_to_show = [col for col in self.columns]
            elif isinstance(self.columns, Callable):
                _cols_to_show = []
                for col in self.df.columns:
                    if self.columns(col):
                        _cols_to_show.append(col)
        else:
            _cols_to_show = self.df.columns
        return _cols_to_show

    @catch_with_error_component_html
    def as_html(self, *args, **kwargs):
        """
       Converts the DataFrame to an HTML table.
       This method formats the DataFrame, converts each row to a dictionary, and then constructs an HTML table
       with the DataFrame's columns as headers and the rows as table data. The table is styled with the "kpi-table" CSS class.

       Returns:
       str: The HTML string of the table.
       """
        self.df = self.method(*args, **kwargs)
        self.limit_data()  # Limit Before formatting, so numbers don't get treated as str for sorting

        self.format_table(self.formatting_method)

        if self.df is None:
            return "<div>No data</div>"

        _cols_to_show = self._columns_to_show()

        columns = ''.join([f'<th>{col.replace("_", " ").upper()}</th>' for col in _cols_to_show])

        rows = []

        if self.coloring is not None:
            columns_to_color = self.coloring.columns
        else:
            columns_to_color = self.df.columns

        for row in self.df.to_dict('records'):

            tr = "<tr>"
            for col in _cols_to_show:

                cell_value = row[col]
                css = ""
                if self.coloring is not None:
                    if columns_to_color is not None:
                        if col in columns_to_color:
                            try:

                                css = self.coloring.method(
                                    cell_value,
                                    target=self.coloring.target,
                                    tolerance=self.coloring.tolerance,
                                    tolerance_percentage=self.coloring.tolerance_percentage,
                                    apply_factor=100,
                                    # This is a hack to make the color_for_bookability work with percentages,
                                    col_name=col,
                                    *args, **kwargs
                                )
                            except Exception as exc:
                                logger.error(f"""
                                Error occurred while coloring {col} Table {self.title=}:
                                ----------------------------------------
                                {exc=}
                                {self.coloring=}
                                """)

                style = ""
                # if self.style_conditional is not None:
                #     print("CALCULATING STYLE?")
                #     style_conditional_method = self.style_conditional.get("method")
                #     column_colors = self.style_conditional.get("kwargs", {})
                #
                #     try:
                #
                #         if isinstance(cell_value, str):
                #             cell_value = cell_value.replace("%", "")
                #             cell_value = str(cell_value).split("\n")[0]
                #             cell_value = float(cell_value)
                #
                #         if col in column_colors:
                #
                #             print(f'{col=}')
                #             color = get_color_for_val_in_range(cell_value, self.df[col].max(), self.df[col].max(), column_colors[col])
                #
                #
                #             style = f"background-color: {color}; color: black;"
                #     except Exception as exc:
                #
                #         print(f'{exc=}')

                cleaned_cell = str(cell_value).replace("\n", "<br>").replace("\r", "<br>")
                tr += f"""<td class="{css} " style=f"{style}">{cleaned_cell}</td>"""
            tr += "</tr>"
            rows.append(tr)
        body = ''.join(rows)

        return f"""
            <h4 class="centered">{self.title}</h4>
           <table class="kpi-table">
               <thead>
                   <tr>
                       {columns}
                   </tr>
               </thead>
                   <tbody>
                        {body}
                   </tbody>
           </table>
       """

    def format_table(self, method: Optional[callable] = None):
        """
        Formats the columns of the DataFrame (`self.df`) using predefined or custom formatting methods.

        Functionality:
        1. Iterates through each column in the DataFrame.
        2. Applies a predefined formatting method from `table_formatting_methods` if the column exists in it.
        3. If a custom formatting method is provided via the `method` parameter, it applies that method to the column.
        4. Logs debug information during the formatting process.
        5. Handles and logs any exceptions that occur during formatting.

        Parameters:
        - method (Optional[callable]): A custom formatting function to apply to the columns. If not provided, only predefined methods are used.

        Instance Variables:
        - `self.df`: The DataFrame whose columns are being formatted.

        Logs:
        - Debug logs for the formatting process.
        - Warnings for any errors encountered during column formatting.

        Returns:
        - `self`: The instance of the class, allowing method chaining.

        Raises:
        - None: Exceptions are caught and logged instead of being raised.

        Example:
            # Assuming `self.df` has columns ['A', 'B'] and `table_formatting_methods` contains a method for 'A':
            self.format_table()
            # Column 'A' will be formatted using the predefined method.
            # Column 'B' will remain unchanged unless a custom method is provided.
        """
        logger.debug(f"""
        Formatting Table
        ------------------

        """)
        for col in self.df.columns:
            try:
                if col in table_formatting_methods:
                    self.df[col] = self.df[col].apply(table_formatting_methods[col])
                elif method:
                    try:
                        self.df[col] = self.df[col].apply(method)
                    except Exception as exc:
                        logger.debug(f"""
                        Error Occurred formatting column {col}:
                        ----------------------------------------
                        {exc}
                        """)

            except Exception as exc:
                logger.warning(f'{col=}{exc=}')
                return self

    def limit_data(self) -> None:
        """
        Limits the rows and columns of the DataFrame (`self.df`) based on specified offsets and limits.
        If a `sort_key` is provided, the DataFrame is sorted accordingly.

        Functionality:
        1. Sorts the DataFrame by `self.sort_key` if provided and valid.
        2. Limits rows and columns using `self.row_offset`, `self.row_limit`, `self.col_offset`, and `self.col_limit`.
        3. Handles errors during sorting and slicing, logging relevant details.

        Instance Variables:
        - `self.df`: The DataFrame to be processed.
        - `self.sort_key`: Column name to sort the DataFrame by.
        - `self.ascending`: Boolean indicating sorting order (ascending if `True`, descending if `False`).
        - `self.row_offset`: Starting index for rows.
        - `self.row_limit`: Maximum number of rows to include.
        - `self.col_offset`: Starting index for columns.
        - `self.col_limit`: Maximum number of columns to include.

        Raises:
        - Exception: If `self.sort_key` is not in the DataFrame's columns.

        Logs:
        - Errors during sorting or slicing, including details about the exception and relevant parameters.

        Example:
            self.sort_key = 'A'
            self.ascending = True
            self.row_offset = 0
            self.row_limit = 10
            self.col_offset = 1
            self.col_limit = 2

            Before:
            self.df:
                A  B  C
            0   3  5  7
            1   1  6  8
            2   2  7  9

            After calling `limit_data`:
            self.df:
                B  C
            1   6  8
            2   7  9
        """

        if self.sort_key is not None:

            if self.sort_key not in self.df.columns:
                logger.error(
                    f"Error while limiting data for Table {self.uid}: Sort key '{self.sort_key}' not in columns {self.df.columns}")
                raise Exception(f"Sort key {self.sort_key} not in columns {self.df.columns}")

            try:
                self.df.sort_values(by=self.sort_key, ascending=self.ascending, inplace=True)

            except Exception as exc:
                logger.error(f"Error sorting data: {exc}, {self.sort_key=}, {self.ascending=}, {self.df.columns=}")
        try:
            _row_start = self.row_offset or 0
            _row_end = _row_start + self.row_limit if self.row_limit else None
            _col_start = self.col_offset or 0
            _col_end = _col_start + self.col_limit if self.col_limit else None

            self.df = self.df.iloc[
                      _row_start:_row_end, _col_start:_col_end
                      ]



        except Exception as exc:
            logger.error(f"Error limiting data: {exc}, {self.row_offset=}, {self.row_limit=}, {self.df.columns=}")

    def get_style_data_conditional(self, *args, **kwargs) -> List:
        logger.debug(f"""
        Getting Style Conditional
        ---------------------------
        {self.coloring=}
        """)

        if self.coloring is None:
            return [
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#fafafa",  # Light grey for odd rows
                },
                {
                    "if": {"state": "active"},
                    "backgroundColor": "#eaeaea",  # Highlight active row
                    "border": "1px solid #ccc",
                },
            ]
        columns = self.df.columns

        style_data_conditional = []
        for col in [
            col for col in self.df.columns if col in self.coloring.columns
        ] if self.coloring.columns else columns:

            try:
                self.df[f'color_{col}'] = self.df[col].apply(
                    lambda x: self.coloring.method(
                        x,
                        target=self.coloring.target,
                        tolerance=self.coloring.tolerance,
                        tolerance_percentage=self.coloring.tolerance_percentage,
                        col_name=col,
                        *args, **kwargs
                    )
                )

                style_data_conditional.extend([
                    {
                        'if': {
                            'filter_query': '{{color_{col}}} eq "green"'.format(col=col),
                            'column_id': col
                        },
                        'backgroundColor': '#ceeadf',
                        'color': '#00644f'
                    },
                    {
                        'if': {
                            'filter_query': '{{color_{col}}} eq "red"'.format(col=col),
                            'column_id': col
                        },
                        'backgroundColor': '#fa7476',
                        'color': '#a00026'
                    },
                    {
                        'if': {
                            'filter_query': '{{color_{col}}} eq "orange"'.format(col=col),
                            'column_id': col
                        },
                        'backgroundColor': '#ffbe7d',
                        'color': '#800041'
                    }

                ]
                )

            except Exception as exc:
                logger.info(
                    f"""'Warning: coloring {col=}, 
                    ------------------------------
                    {self.coloring.method=}, {self.coloring.target=}, {self.coloring.tolerance=}, {self.coloring.tolerance_percentage=}
                    {exc=}
                    """

                )

        return style_data_conditional

class TableWithPagination(Table): # TODO: work on this, it works but should be improved
    def as_dash(self, *args, **kwargs):
        self.row_limit = None
        return super().as_dash(*args, **kwargs)
    def as_html(self, *args, **kwargs):
        self.row_limit = 10
        return super().as_html(*args, **kwargs)
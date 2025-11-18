from __future__ import annotations

import logging
import uuid
from typing import Callable, List, Optional, Union, ClassVar

logger = logging.getLogger(__name__)
try:
    # Not required for CF
    import dash_bootstrap_components as dbc
    from dash import html
except ImportError:
    ...

from pydantic import Field, BaseModel, field_validator, field_serializer

from helpers import performance_timer_with_logger, find_function_globally


def create_id() -> str:
    """Create a unique ID for a component."""
    return str(uuid.uuid4())


class UIBaseComponent(BaseModel):
    children: List = Field(default=None, description="List of children components.")
    class_name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    hover: Optional[bool] = Field(default=False)
    layout: Optional[str] = Field(default="")
    method: Optional[Union[Callable, UIBaseComponent, str]] = Field(default=None)
    style: str = Field(default="")
    uid: str = Field(default_factory=create_id)
    model_config = {
        "arbitrary_types_allowed": True
    }
    instance_count: ClassVar[int] = 0
    status: Optional[str] = Field(default=None)
    children_over_method: Optional[bool] = Field(default=True)
    sql: Optional[str] = Field(default=None)

    @field_validator("children", mode="before")
    @classmethod
    def validate_children(cls, v: str) -> Optional[List]:
        if v is None:
            return []
        elif not isinstance(v, list):
            return [v]
        else:
            return v

    @performance_timer_with_logger
    def calculate_children(self, *args, **kwargs) -> None:
        """Calculate children components. If a method is provided, call it to get the children.
        """
        if isinstance(self.method, Callable):
            self.children = self.method(*args, **kwargs)
        elif isinstance(self.method, str):
            self.method = find_function_globally(self.method)

            if self.method is None:
                raise ValueError(f"Method {self.method} not found in any module.")
            else:
                if hasattr(self, "type"):
                    if self.type == "big-statistic":
                        self.children = [
                            html.Div(
                                children=self.method(*args, **kwargs),
                                className="kpi-big-statistic"
                            )
                        ]
                    else:
                        self.children = self.method(*args, **kwargs)
                else:
                    self.children = self.method(*args, **kwargs)

        elif self.children is not None and len(self.children) > 0 and self.children_over_method:
            ...
        elif self.method is None:
            self.children = []


        else:
            self.children = []

    @performance_timer_with_logger
    def as_dash(self, *args, **kwargs) -> html.Div:
        """Render the component as a Dash component. If the children are UIBaseComponent instances, render them as Dash
        components as well.
        """

        UIBaseComponent.instance_count += 1

        debug_div = [
            html.Div(
                className="debug-component",
                children=[
                    f"""{self.uid=},
                    {UIBaseComponent.instance_count=},
                    {self.__class__.__name__=}""",


                ],
                id={"type": "component-debug", "index": UIBaseComponent.instance_count}
            )
        ]

        self.calculate_children(*args, **kwargs)
        

        if self.hover:
            self.children.extend(
                [
                    html.Div(
                        className="tooltip-header",
                        children=html.Div(
                            "ℹ️",
                            # style={
                            #     "position": "absolute",
                            #     "top": "10px",
                            #     "right": "10px",
                            #     "cursor": "pointer",
                            #     "fontSize": "1rem",
                            # },
                            id=f"{self.uid}-tooltip-trigger",
                        ),
                    ),
                    dbc.Tooltip(
                        [
                            html.Span(self.uid, className="tooltip-title"),
                            html.Br(),
                            html.Span(self.description, className="tooltip-description")
                        ],
                        target=f"{self.uid}-tooltip-trigger",  # Target the button by its ID
                        placement="top"  # Position of the tooltip (top, bottom, left, right)
                    )
                ]
            )
        children = []
        for c in self.children:
            if isinstance(c, UIBaseComponent):
                _c = c.as_dash(*args, **kwargs)
                if isinstance(_c, list):
                    children.extend(_c)
                else:
                    children.append(_c)
            else:
                children.append(c)
        debug_div[0].children.append(self.status)


        # Ensure kwargs is a dict
        if kwargs is None:
            kwargs = {}
        debug_div[0].children.append(kwargs.get("sql"))
        return html.Div(
            id=self.uid,
            className=self.calculate_class_name(),
            children=children + debug_div
        )

    @performance_timer_with_logger
    def as_pdf(self, *args, **kwargs):
        """Render the component as a PDF. If the children are UIBaseComponent instances, render them as PDF as well."""
        ...

    @classmethod
    def to_html(cls, el: Union[
        html.Div, html.H1, html.H2, html.H3, html.H4, html.H5, html.Div, html.Span, html.P, html.Br, html.A]) -> str:
        """Convert a component to an HTML string."""
        if el is None:
            return ""
        elif isinstance(el, str):
            return el

        elif isinstance(el, html.H1):
            return "<h1>" + "".join([UIBaseComponent.to_html(c) for c in el.children]) + "</h1>"
        elif isinstance(el, html.H2):
            return "<h2>" + "".join([UIBaseComponent.to_html(c) for c in el.children]) + "</h2>"
        elif isinstance(el, html.H3):
            return "<h3>" + "".join([UIBaseComponent.to_html(c) for c in el.children]) + "</h3>"
        elif isinstance(el, html.H4):
            return "<h4>" + "".join([UIBaseComponent.to_html(c) for c in el.children]) + "</h4>"
        elif isinstance(el, html.H5):
            return "<h5>" + "".join([UIBaseComponent.to_html(c) for c in el.children]) + "</h5>"
        elif isinstance(el, html.Div):
            return f"""<div class="{getattr(el, "className", None) or ''}">""" + "".join(
                [UIBaseComponent.to_html(c) for c in el.children]) + """</div>"""
        elif isinstance(el, html.Span):
            return f"""<span class="{getattr(el, "className", None) or ''}">""" + "".join(
                [UIBaseComponent.to_html(c) for c in el.children]) + """</span>"""
        elif isinstance(el, html.P):
            return f"""<p class="{getattr(el, "className", None) or ''}">""" + "".join(
                [UIBaseComponent.to_html(c) for c in el.children]) + """</p>"""
        elif isinstance(el, html.Br):
            return "<br>"
        elif isinstance(el, html.A):
            return f"""<a href="{getattr(el, "href", None)}" class="{getattr(el, "className", None) or ''}">""" + "".join(
                [UIBaseComponent.to_html(c) for c in el.children]) + """</a>"""
        else:
            logger.error(f"Unknown component type: {type(el)}; will not be printed to PDF.")
            return ""

    @performance_timer_with_logger
    def as_html(self, *args, **kwargs) -> str:
        """Render the component as an HTML string. If the children are UIBaseComponent instances, render them as HTML"""
        kwargs.update({"printable": True})
        self.calculate_children(*args, **kwargs)
        if self.children is None:
            children_html = "[EMPTY]"
        else:
            aux = []
            for child in self.children or []:
                if child is None:
                    ...
                elif isinstance(child, UIBaseComponent):
                    aux.append(child.as_html(*args, **kwargs))
                elif isinstance(child, str):
                    aux.append(child)
                else:
                    aux.append(UIBaseComponent.to_html(child))

            children_html = "".join([el for el in aux if el is not None])
        if hasattr(self, "type"):
            if self.type == "big-statistic":
                return f"""
                    <div class="kpi-card">
                        {children_html}
                    </div>
                """

        return f"""
                <div class="{self.class_name}" style="{self.style}">
                    {children_html}
                </div>
        """

    def calculate_class_name(self):
        return f"{self.class_name or ''} {self.layout or ''}"

    @field_serializer('method', when_used="json")
    def serialize_method(self, method):
        if method is None:
            return None
        return f"{method.__module__}.{method.__qualname__}"

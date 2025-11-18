"""
"""
from __future__ import annotations

import logging
from typing import List, Union, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field

from schemas.components.card import Card
from schemas.components.ui_base_component import UIBaseComponent

logger = logging.getLogger(__name__)


class Col(UIBaseComponent):
    class_name: str = Field(default="col")
    children: List[Union[Col, Row, Card]] = Field(default_factory=list)
    col: bool = True

    def as_html(self, *args, **kwargs) -> str:
        _css = list(set([x for x in self.class_name.split(" ") if "col-kpi" in x]))

        if len(_css) > 0:
            col_x = int(_css[0].split("-")[-1])
        else:
            col_x = 12

        kwargs.update(
            {"col_x": col_x}
        )
        return super().as_html(*args, **kwargs)


class Div(UIBaseComponent):
    ...


class Row(UIBaseComponent):
    class_name: str = Field(default="row centered")
    children: List[Union[Col, Row, Card]] = Field(default_factory=list)
    distribute_content: Optional[str] = Field(
        default=None)  # This is quite hardcoded if we want to extend the usage we need to extend code

    def as_dash(self, *args, **kwargs) -> html.Div:
        try:
            if self.distribute_content is None:
                return super().as_dash(*args, **kwargs)
            else:
                super().calculate_children(*args, **kwargs)

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

                return html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className=self.distribute_content,
                            children=Card(
                                children=child
                            ).as_dash(*args, **kwargs)
                        )
                        for child in children
                    ]
                )
        except Exception as exc:

            return html.Div(dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("❌ ", className="card-title"),
                        html.P(str(exc), className="card-text"),
                    ]
                ),
                color="danger",
                inverse=False,
                outline=True
            )
            )

    def as_html(self, *args, **kwargs) -> str:
        try:
            if self.distribute_content is None:
                return super().as_html(*args, **kwargs)
            else:
                super().calculate_children(*args, **kwargs)

                if isinstance(self.distribute_content, str):
                    self.distribute_content = [self.distribute_content for _ in self.children]

                children_html = []
                for child, class_name in zip(self.children, self.distribute_content):
                    _css = list(set([x for x in class_name.split(" ") if "col-kpi" in x]))
                    if len(_css) > 0:
                        col_x = int(_css[0].split("-")[-1])
                    else:
                        col_x = 12

                    kwargs.update(
                        {"col_x": col_x}
                    )
                    child_html = child.as_html(*args, **kwargs)
                    children_html.append(child_html)

                return f"""
                <div class="row">
                    {
                "".join(
                    [
                        f'''
                                <div class="{class_name}">
                                    <div class="kpi-card card">
                                        {child}
                                    </div>
                                </div>
                            '''
                        for child, class_name in zip(children_html, self.distribute_content)
                    ]
                )
                }
                </div>
                """
        except Exception as exc:

            print(f'{exc=}')

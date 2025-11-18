import logging
from typing import List, Optional, Dict, Callable, Union, ClassVar

from dash import dcc
from dash import html
from pydantic import Field

from schemas.components.card import Card
from schemas.components.error import catch_with_error_component_dash, catch_with_error_component_html
from schemas.components.row import Row, Div
from schemas.components.ui_base_component import UIBaseComponent

logger = logging.getLogger(__name__)


class Tab(UIBaseComponent):
    children: Union[List[Union[Row, Card, Div, str]], Row] = Field(default_factory=list)
    class_name: str = Field(default="tab spark-tabs__panel")
    header_method: Optional[Callable] = Field(default=None)
    instance_count: ClassVar[int] = 0
    label: str = Field(default="Tab")
    params: Optional[Dict] = Field(default_factory=dict)

    @catch_with_error_component_dash
    def as_dash(self, *args, **kwargs):  # -> html.Div:
        Tab.instance_count += 1
        logger.debug(f"""
        =========================================
        TAB: {self.label}
        =========================================
        {self.uid}, {self.label}, {self.params}
        """
                     )
        if self.params.get("pcc", None) is not None:
            self.label += " - " + self.params.get("pcc")
        kwargs.update(self.params)
        try:
            self.calculate_children(*args, **kwargs)
            kwargs.update({"tab_name": self.label})

            return dcc.Tab(
                label=self.label,
                className=f"{self.class_name} spark-tabs__tab",
                children=[
                    html.Div(
                        id=f"{self.uid}-content",
                        className="tab-pane active",
                        role="tabpanel",
                        children=[
                                     html.Div(
                                         className="spark-panel spark-mar-t-1 spark-text-center tab-content-header kpi-card",
                                         children=self.header_method(*args, **kwargs) if self.header_method else None
                                     ) if self.header_method is not None else None

                                 ] + [
                                     c.as_dash(*args, **kwargs) if isinstance(c, UIBaseComponent) else c for c in
                                     self.children
                                 ]

                    )
                ],
                id={"type": "tab", "index": Tab.instance_count},
                selected_style={"max-width": "100%"},
                style={"max-width": "100%"}

            )
        except Exception as exc:

            print(f'Tab as_dash {exc=}')
            return dcc.Tab(
                label=f" ❌ {self.label}",
                className=self.class_name,
                children=[
                    f"error: {exc=}"
                ],
                id={"type": "tab", "index": Tab.instance_count},

            )

    @catch_with_error_component_html
    def as_html(self, *args, **kwargs) -> str:
        try:
            if self.params.get("pcc", None) is not None:  # TODO: move to vbp report
                self.label += " - " + self.params.get("pcc")
            kwargs.update(self.params)
            aux = []

            for c in self.children or []:

                try:
                    if c is None:
                        ...
                    elif isinstance(c, UIBaseComponent):
                        _html = c.as_html(*args, **kwargs)

                        if _html is None:
                            ...
                        else:
                            aux.append(_html)
                    else:
                        aux.append(c)
                except Exception as exc:
                    print(f"Error on Tab as_html: {exc=}")

            children_html_ = "".join(aux)
            return f"""
                <section>
                        <div class="{self.class_name}">                
                            <h3>{self.label} </h3>
                            {children_html_}
                        </div>
                </section>
            """
        except Exception as exc:
            logger.error(f"Tab as_html {exc=}")
            return f"""
                <section>
                        <div class="{self.class_name}">                
                            <h3>{self.label} </h3>
                            <h3>{exc} </h3>
                        </div>
                </section>
            """

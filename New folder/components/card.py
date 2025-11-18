import logging
from typing import Optional, Callable

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field

from helpers import performance_timer_with_logger
from schemas import available_methods
from schemas.components.error import catch_with_error_component_html
from schemas.components.ui_base_component import UIBaseComponent

logger = logging.getLogger(__name__)
_ = available_methods  # This is a hack to prevent the import from being removed by isort


class Card(UIBaseComponent):
    class_name: str = Field(default="spark-panel__content kpi-card")
    footer: Optional[UIBaseComponent] = Field(default=None)
    title: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)

    def as_dash(self, *args, **kwargs) -> html.Div:

        logger.debug(f"""        
        CARD AS DASH
        -----------------
        {self.title=}
        {self.class_name=}        
        """)


        try:
            return html.Div(
                className="spark-mar-1 spark-panel spark-panel--card" + (f" {self.layout}" if self.layout else ""),
                children=super().as_dash(*args, **kwargs),
                style={"width": "auto"}

            )
        except Exception as exc:
            logger.error(f"Error in Card.as_dash: {exc}")
            return html.Div(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H2(self.title or "", className="card-title"),
                            html.H4("❌ ", className="card-title"),
                            html.P(str(exc), className="card-text"),
                        ]
                    ),
                    color="danger",
                    inverse=False,
                    outline=True
                ),
                className="spark-mar-1 spark-panel spark-panel--card" + (f" {self.layout}" if self.layout else "")
            )

    @catch_with_error_component_html
    def as_html(self, *args, **kwargs) -> str:
        self.class_name = "kpi-card card"
        return super().as_html(*args, **kwargs)

    @performance_timer_with_logger
    def calculate_children(self, *args, **kwargs) -> None:
        """Calculate children components. If a method is provided, call it to get the children.
        """
        try:
            super().calculate_children(*args, **kwargs)
        except Exception as exc:
            raise exc

        if self.title is not None:
            self.children = self.children or []
            self.children.insert(0, html.H4(self.title, className="kpi-card-title"))

        if self.footer is not None:
            if isinstance(self.footer, Callable):
                calculated_footer = self.footer()
                self.children.append(
                    calculated_footer
                )
            elif isinstance(self.footer, UIBaseComponent):
                self.footer.calculate_children(*args, **kwargs)

                self.children.extend(
                    self.footer.children
                )


            else:
                calculated_footer = self.footer

                self.children.append(
                    calculated_footer
                )

    def serialize(self):
        return super().serialize()

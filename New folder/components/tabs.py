import logging
from typing import List, Optional

from dash import dcc, html
from pydantic import Field

from schemas.components.error import catch_with_error_component_dash, catch_with_error_component_html
from schemas.components.tab import Tab
from schemas.components.ui_base_component import UIBaseComponent

logger = logging.getLogger(__name__)


class Tabs(UIBaseComponent):
    children: List[Tab] = Field(default_factory=list, description="List of tabs to display.")
    class_name: Optional[str] = Field(default="spark-tabs")

    @catch_with_error_component_dash
    def as_dash(self, *args, **kwargs) ->html.Nav:
        try:
            self.calculate_children(*args, **kwargs)
        except Exception as exc:
            logger.error(f"Error calculating children for Tabs: {exc}")
            self.children = []
        return html.Nav(
            className="spark-tabs__nav katana-docs-tabs__nav",
            role="menubar",
            children=html.Div(
                className="",
                children=dcc.Tabs(
                    id=self.uid,
                    className=self.class_name,
                    children=[
                        tab.as_dash(*args, **kwargs) for tab in self.children
                    ]
                )

            )
        )

    # @catch_with_error_component_html
    def as_html(self, *args, **kwargs) -> str:
        try:
            self.calculate_children(*args, **kwargs)

            return f"""
                <div class="{self.class_name}">
                    {
                        "".join(
                                [
                                    tab.as_html(*args, **kwargs)
                                    for tab in self.children
                                ]
                        )
                    }
                </div>
            """
        except Exception as exc:
            logger.error(f"{exc=}")
            return "ERROR: Could not render Tabs."

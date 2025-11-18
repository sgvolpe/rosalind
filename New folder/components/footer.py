from typing import List, Optional

from dash import html
from pydantic import Field

from schemas.components.error import catch_with_error_component_dash, catch_with_error_component_html
from schemas.components.ui_base_component import UIBaseComponent


class Footer(UIBaseComponent):
    children: Optional[List] = Field(default_factory=list)

    @catch_with_error_component_dash
    def as_dash(self, *args, **kwargs) -> html.Div:
        sabre_link = html.A(
            href="https://www.sabre.com",
            className="spark-footer__logo spark-hidden--lte-sm",
            # ariaLabel="Visit the Sabre website",
            children=[
                html.I(
                    className="spark-logo spark-logo--sabre spark-logo--xs")
            ]
        )
        footer_content = html.Div(
            className="spark-footer__content",
            children=[
                html.Div(
                    # className="spark-footer__copyright", children=["© Sabre"]
                ),
                html.Ul(
                    className="spark-footer__list",
                    children=[
                        html.Li(
                            className="spark-footer__list-item",
                            children=[
                                html.A("Contact Us", href="mailto:ocean.team@sabre.com")
                            ]
                        ),
                    ]
                )
            ]
        )
        other_links = html.Ul(
            className="spark-footer__list spark-footer__list--right spark-footer__list--icons",
            children=[
                html.Li(
                    className="spark-footer__list-item",
                    children=[child]
                )
                for child in self.children
            ]

        )
        container = html.Div(
            className="container",
            children=[sabre_link, footer_content, other_links]
        )
        return html.Div(
            className="spark-footer footer",
            children=[
                container

            ],
        )


    @catch_with_error_component_html
    def as_html(self, *args, **kwargs) -> str:
        return super().as_html(*args, **kwargs)

import logging
import traceback
from typing import Optional

import dash_bootstrap_components as dbc
from dash import html, dcc
from pydantic import Field

from helpers import performance_timer_with_logger
from schemas.components.ui_base_component import UIBaseComponent

logger = logging.getLogger(__name__)
icons = {
    "info": "ℹ",  # Information icon
    "warning": "⚠️",  # Warning icon
    "danger": "❌",  # Error icon
    "success": "✅"  # Success icon
}


class ErrorComponent(UIBaseComponent):
    level: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)

    @performance_timer_with_logger
    def as_dash(self, *args, **kwargs):
        # Default to 'info' if level is not recognized
        icon = icons.get(self.level, icons["info"])
        return html.Div(
            dbc.Alert(
                [
                    html.Span(icon, style={"margin-right": "10px"}),  # Add icon with spacing
                    self.message
                ],
                color=self.level,  # Set the color dynamically
                dismissable=True,  # Allow the alert to be closed
            )
        )

    @performance_timer_with_logger
    def as_html(self, *args, **kwargs) -> str:
        icon = icons.get(self.level, icons["info"])
        # <span class="alert-icon" >{icon}</span>
        return f"""
            <div class="alert alert-{self.level} >            
            {self.message}
        </div>
        """

class ErrorCard(ErrorComponent):
    @performance_timer_with_logger
    def as_dash(self, *args, **kwargs):
        return html.Div(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Error!", className="card-title"),
                        html.P(self.message, className="card-text"),
                    ]
                ),
                color="danger",
                inverse=False,
                outline=True
            )
        )

    @performance_timer_with_logger
    def as_html(self, *args, **kwargs) -> str:
        return f"""
            <div class="card text-white bg-danger mb-3">
              <div class="card-body">
                <h5 class="card-title">Error</h5>
                <p class="card-text">{self.message}</p>
                </div>
            </div>
            """


class ErrorChart(ErrorComponent):
    @performance_timer_with_logger
    def as_dash(self, *args, **kwargs):
        return html.Div(
            html.H2("error:", self.title or ""),
            html.H4("Error Chart!", className="card-title"),
            dcc.Graph()

        )

    @performance_timer_with_logger
    def as_html(self, *args, **kwargs) -> str:
        return f"""
            <div class="card text-white bg-danger mb-3">
              <div class="card-body">
                <h5 class="card-title">Error</h5>
                <p class="card-text">{self.message}</p>
                </div>
            </div>
            """

class ErrorTab(ErrorComponent):
    @performance_timer_with_logger
    def as_dash(self, *args, **kwargs):

        return html.Div(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Error Tab!", className="card-title"),
                        html.P(self.message, className="card-text"),
                    ]
                ),
                color="danger",
                inverse=True,
            )
        )

    @performance_timer_with_logger
    def as_html(self, *args, **kwargs) -> str:
        return f"""
            <div class="card text-white bg-danger mb-3">
              <div class="card-body">
                <h5 class="card-title"""

@performance_timer_with_logger
def catch_with_error_component_dash(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            class_name = func.__qualname__.split(".")[0]

            message = f"""
            Error rendering component as Dash: 
            {exc=} 
            {func=}
            {func.__name__=}
            {class_name=}
            
            """
            logger.error(message)



            return {
                "Card": ErrorCard,
                "Chart": ErrorChart,
                "Tab": ErrorTab,
            }.get(class_name, ErrorComponent)(level="danger", message=message).as_dash()



    return wrapper


@performance_timer_with_logger
def catch_with_error_component_html(func):
    def wrapper(*args, **kwargs):
        context = kwargs.get("context", [])
        try:
            res = func(*args, **kwargs)
            context.append(
                {"status": "success",
                 "message": "ok"
                 }
            )
            return res
        except Exception as exc:
            raise
            logger.error(f"""
            Error Catched for HTML conversion
            ---------------------------------
            {func=}
            {exc=}
            """)
            traceback.print_exc()
            context.append(
                {"status": "error",
                 "message": exc
                 }
            )
            return ErrorComponent(level="danger", message=f"Error rendering component: {exc}").as_html()

    return wrapper

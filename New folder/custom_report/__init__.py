from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path
from typing import Optional, List, Union, Callable, Type, Any

from dash.html import Div, H2, H4, P
from dash_bootstrap_components import Card, Col, Row, Tab, CardBody
from pydantic import BaseModel, Field, field_validator, model_validator
from weasyprint import CSS, HTML

from helpers import find_function_globally


class ComponentBase(BaseModel):
    dash_class: Optional[Type] = Field(default=None)
    children: Union[List[Any], Any] = Field(default_factory=list)
    class_name: Optional[str] = Field(default=None)
    method: Optional[Union[str, Callable]] = Field(default=None)
    html_tag: str = Field(default="div")
    uid: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def build_self(self):
        logging.debug(f"Building self {self.__class__.__name__}")
        return self

    @field_validator("children", mode="before")
    @classmethod
    def validate_children(cls, v: Any) -> List[Any]:
        if v is None:
            return None
        elif not isinstance(v, list):
            return [v]
        else:
            return v

    def set_method(self):
        if self.method is not None:
            if isinstance(self.method, str):
                self.method = find_function_globally(self.method)
                logging.debug(f'METHOD UPDATED TO: {self.method=}')

    def as_dash(self, *args, **kwargs) -> Any:
        logging.debug(f'Building {self.__class__.__name__} as dash component...')
        try:
            self.set_method()

            if isinstance(self.method, Callable):
                self.children = self.method(*args, **kwargs)
            new_children = []
            for i, child in enumerate(self.children):
                if isinstance(child, ComponentBase):
                    dashed_child = child.as_dash(*args, **kwargs)
                    if isinstance(dashed_child, list):
                        logging.debug(f'{dashed_child=} is list, extending children...')
                        # self.children.pop(i)
                        new_children.extend(dashed_child)
                    else:
                        new_children.append(dashed_child)

                else:
                    new_children.append(child)
                    print(f"IT IS NOT COMPONENT BASE: {type(child)=}")
            return self.dash_class(
                children=new_children,
                className=self.class_name,
            )
        except Exception as exc:
            return Div(
                Card(
                    CardBody(
                        [
                            H4("Error!", className="card-title"),
                            P(f"Error {exc}", className="card-text"),
                        ]
                    ),
                    color="danger",
                    inverse=False,
                    outline=True
                )
            )

    def as_html(self, *args, **kwargs) -> Any:
        logging.debug(f"""
        Building {self.__class__.__name__} as html component...
        {self.method=}
        """)
        self.set_method()

        if isinstance(self.method, Callable):
            self.children = self.method(*args, **kwargs)

            logging.debug(f"""
                    {self.method=}
                    {self.children=}
            """)
        elif isinstance(self.method, ComponentBase):
            self.children = [self.method]

        rendered_children = []
        for i, child in enumerate(self.children):
            if isinstance(child, ComponentBase):
                logging.debug(f"""
                {child=} is ComponentBase, 
                converting to html...
""")
                # self.children[i] = child.as_html(*args, **kwargs)
                html_child = child.as_html(*args, **kwargs)
                logging.debug(f'{type(html_child)=}')
                rendered_children.append(html_child)
            elif isinstance(child, str):
                rendered_children.append(child)
            else:
                logging.debug(f"It is not a ComponentBase: {type(child)}")
        return f"""<{self.html_tag} id="{self.uid or ''}" class="{self.class_name or ''}">{''.join(rendered_children)}</{self.html_tag}>"""


class DivComponent(ComponentBase):
    dash_class: Optional[Type] = Field(default=Div)
    class_name: Optional[str] = Field(default="")
    html_tag: str = Field(default="Div")


class H2Component(ComponentBase):
    dash_class: Optional[Type] = Field(default=H2)
    class_name: Optional[str] = Field(default="")
    html_tag: str = Field(default="h2")


class CardComponent(ComponentBase):
    dash_class: Optional[Type] = Field(default=Card)
    class_name: Optional[str] = Field(default="spark-panel__content kpi-card")

    def as_html(self, *args, **kwargs) -> Any:

        logging.debug(f"""
            Building {self.__class__.__name__} as html component...
            {self.method=}
            """)
        self.set_method()

        if isinstance(self.method, Callable):
            self.children = self.method(*args, **kwargs)

            # logging.debug(f"""
            #             {self.method=}
            #             {self.children=}
            #     """)
        # elif isinstance(self.method, ComponentBase):
        #     self.children = [self.method]

        rendered_children = []
        for i, child in enumerate(self.children):
            if isinstance(child, ComponentBase):
                logging.debug(f"""
                     is ComponentBase, 
                    converting to html...
    """)
                rendered_children.append(child.as_html(*args, **kwargs))

        return f"""<{self.html_tag} id="{self.uid or ''}" class="{self.class_name or ''}">{''.join(rendered_children)}</{self.html_tag}>"""


class ColComponent(ComponentBase):
    children: List[Union[CardComponent, RowComponent,]] = Field(default_factory=list)
    dash_class: Optional[Type] = Field(default=Col)
    class_name: Optional[str] = Field(default="col")


class RowComponent(ComponentBase):
    children: List[ColComponent] = Field(default_factory=list)
    dash_class: Optional[Type] = Field(default=Row)
    class_name: Optional[str] = Field(default="row centered")


class TabComponent(ComponentBase):
    title: Optional[str] = Field(default=None)
    children: List[RowComponent] = Field(default_factory=list)
    dash_class: Optional[Type] = Field(default=Tab)
    class_name: Optional[str] = Field(default="parent-hover parent-col-hover spark-tab tab spark-tabs__panel")


class TabsComponent(ComponentBase):
    title: Optional[str] = Field(default=None)
    children: List[TabComponent] = Field(default_factory=list)
    dash_class: Optional[Type] = Field(default=Div)


class CustomReport(ComponentBase):
    title: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None)
    tabs: Optional[List[TabComponent]] = Field(default=None)
    dash_class: Optional[Type] = Field(default=Div)
    css_files: Optional[List[str]] = Field(default=["kpi_disclaimer.css", "report_pdf.css"])

    @model_validator(mode="after")
    def build_self(self):
        self.children = self.tabs

        return self

    def as_pdf(self, save_to_tmp: bool = True, *args, **kwargs) -> tuple[Union[Path, BytesIO], str]:

        try:
            stylesheets = []
            try:
                css_base_path = Path() / "static" / "css"
                if not css_base_path.exists():
                    css_base_path = Path() / "ocean_reports" / "static" / "css"
                for css_file in self.css_files:
                    stylesheets.append(CSS(string=(css_base_path / css_file).read_text()))

            except Exception as exc:
                logging.error(f"Error loading custom CSS: {exc}")

            f_name = "Test_report.pdf"

            try:
                report_html = HTML(string=self.as_html(*args, **kwargs))
                report_html.metadata = {
                    "Title": self.title,
                    "Author": "Ocean.Team@Sabre.com",
                    "Subject": "Report",
                    "Keywords": "KPI, Report, Ocean, Sabre",
                    # 'CreationDate': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            except Exception as exc:
                raise Exception(f"Error creating HTML: {exc}")

            if save_to_tmp:
                try:
                    pdf_path = Path() / "tmp" / "pdfs"
                    pdf_path.mkdir(parents=True, exist_ok=True)
                    out_path = pdf_path / f_name

                    report_html.write_pdf(out_path, stylesheets=stylesheets)
                    print(f'PDF SAVED TO{out_path=}')
                    return out_path, f_name
                except Exception as exc:
                    logging.error(f"Error saving PDF to tmp: {exc}")
                    raise Exception(f"Error saving PDF to tmp: {exc}")
            else:
                try:
                    pdf_buffer = BytesIO()
                    report_html.write_pdf(
                        pdf_buffer,
                        stylesheets=stylesheets,
                    )
                    pdf_buffer.seek(0)

                    return pdf_buffer, f_name
                except Exception as exc:
                    logging.error(f"Error creating PDF buffer: {exc}")
                    raise Exception(f"Error creating PDF buffer: {exc}")
        except Exception as exc:
            logging.error(f"Error creating PDF: {exc}")
            raise Exception(f"Error creating PDF: {exc=}")

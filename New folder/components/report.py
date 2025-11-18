import functools
import json
import logging
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, List, ClassVar, Any

from dash import html
from dash.html import Main
from pydantic import model_validator, Field
from weasyprint import CSS, HTML

from app.core.config import settings
from common_params import DATE_FORMAT
from custom_exceptions import NotFoundException
from helpers import performance_timer_with_logger, upload_blob
from ocean_firestore import get_configuration_from_firestore, get_dates_and_agency_name_from_firestore_config
from schemas.components.footer import Footer
from schemas.components.tabs import Tabs
from schemas.components.ui_base_component import UIBaseComponent
from schemas.data_sources.data_sources import DataFrameFilter
from schemas.report_context import ReportContext

logger = logging.getLogger(__name__)
template_path = (Path() / "static" / "templates" / "kpi").resolve()

test_configuration_id_list = ["vbp--test1", ]

default_disclaimer = """Disclaimer: This data is provided for your information and monitoring purposes only and shall 
           not be used for billing purposes.
"""


def inspect_pdf(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        ts = time.perf_counter()

        pdf_buffer, f_name = fn(*args, **kwargs)
        # TODO: for some reason count pdf pages fails without printing msg error
        # actual_page_count = count_pdf_pages(pdf_buffer)
        # # if page_count := kwargs.get("page_count", None):
        # #     assert actual_page_count == page_count, f"Page count mismatch: {actual_page_count} != {page_count}"
        # print(f"{f_name}: {actual_page_count} PAges : {time.perf_counter() - ts:.2f} secs  ")

        return pdf_buffer, f_name

    return wrapper


class Report(UIBaseComponent):
    action_buttons: Optional[List[Any]] = Field(default_factory=list)
    agency_name: Optional[str] = Field(default=None)
    configuration_id: Optional[str] = Field(default=None)
    data_source_filters: Optional[List[DataFrameFilter]] = Field(default=None)
    date_end: Optional[str] = Field(default=None)
    date_start: Optional[str] = Field(default=None)
    disclaimer: Optional[str] = Field(default=default_disclaimer)
    glossary: Optional[dict] = Field(default_factory=dict)
    include_glossary: Optional[bool] = Field(default=False)
    report_type: Optional[str] = Field(default="ocean")
    requires_configuration_id: ClassVar[bool] = True
    tabs: Optional[Tabs] = Field(default_factory=Tabs)
    template_id: Optional[str] = Field(default=None, description="Template ID for the report")
    title: Optional[str] = Field(default="Ocean Report")
    css_files: Optional[List[str]] = Field(default=["kpi_disclaimer.css", "report_pdf.css"])
    submit_form: Optional[Any] = Field(default=None)



    def read_tabs(self):
        full_path = template_path / f"{self.template_id}.json"
        if not full_path.exists():
            full_path = Path() / "ocean_reports" / "static" / "templates" / "kpi" / f"{self.template_id}.json"
        if full_path.exists():
            with open(full_path) as f:
                js = json.load(f)
                self.tabs = Tabs(**js["tabs"])
        else:
            raise Exception(f"{full_path} path does not exist")

    def as_dash(self, *args, **kwargs):

        kwargs.update(
            **{
                "agency_name": self.agency_name,
                "configuration_id": self.configuration_id,
                "date_start": kwargs.get("date_start", None) or self.date_start,
                "date_end": kwargs.get("date_end", None) or self.date_end,
                "data_source_filters": self.data_source_filters
            }
        )
        try:
            _tabs = [
                self.tabs.as_dash(*args, **kwargs)
            ]

            _html = html.Div(
                [
                    Main(
                        className="row",
                        children=[
                            html.Div(
                                className="heading",
                                children=self.build_header()
                            ),
                            html.Div(
                                className="spark-panel__content",
                                children=_tabs
                            ),
                            Footer(children=self.disclaimer).as_dash(*args, **kwargs)
                        ],
                        style={"margin": "2rem"}
                    )
                ]
            )

            return _html

        except Exception as exc:
            print(f"Error building report as dash: {exc}")
            logger.error(f"KPI REPORT AS DASH: {exc}")

    def build_header(self):
        return []
        return [
            html.H1(self.agency_name, className="spark-main__title"),
            html.P(f"Report dates: {self.date_start} to {self.date_end}"),
            html.P(f"Template id: {self.template_id}"),
            html.Div(

                # TODO: RED FLAGS AND ALERTING
                # children=[
                #     json.dumps(kwargs.get("context").red_flags, indent=4)
                # ]
            )
        ]

    def read_configuration_from_firestore(self, *args, **kwargs):
        logger.debug(f"""READING FIRESTORE
        -------------------------
        {kwargs=}
        """)

        if self.configuration_id in test_configuration_id_list:
            return
        try:
            config: dict = get_configuration_from_firestore(self.configuration_id)
            _date_start, _date_end, _agency_name = get_dates_and_agency_name_from_firestore_config(config)
            (
                self.date_start, self.date_end, self.agency_name
            ) = (
                _date_start or self.date_start, _date_end or self.date_end, _agency_name or self.agency_name
            )
            custom_fields = config.get("customFields", None)

            if custom_fields is not None:
                self.template_id = custom_fields.get("deliveryReportName", None)

        except NotFoundException as exc:
            logger.error(f"Configuration ID: {self.configuration_id} not found. {exc=}")
            raise exc

    @performance_timer_with_logger
    def as_html(self, *args, **kwargs):
        kwargs.update(
            **{
                "agency_name": self.agency_name,
                "data_source_filters": self.data_source_filters,
                "configuration_id": self.configuration_id,
                "date_start": kwargs.get("date_start", None) or self.date_start,
                "date_end": kwargs.get("date_end", None) or self.date_end,

            }
        )
        logger.debug(f"""
        AS HTML
        --------------
        {kwargs=}  
        """)

        today = datetime.today()
        current_date = today.strftime(DATE_FORMAT)

        img_path = Path() / "static" / "img"
        if not img_path.exists():
            img_path = Path() / "ocean_reports" / "static" / "img"

        # with open(img_path / "vbp_cover.txt") as f:
        #     cover_img = f.read()
        with open(img_path / "sabre_logo.txt") as f:
            sabre_logo_str = f.read()

        try:
            cover = self.build_cover(*args, **kwargs)
        except Exception as exc:
            logger.error(f"Error building cover: {exc}")
            cover = ""
        try:
            last_page = f"""
                <div class="last-page">
                    <div class="last-page-content">
                        <h1>End of Report</h1>
                        <img src="{sabre_logo_str}" alt="Sabre">
                    </div>
                </div>
            """
        except Exception as exc:
            logger.error(f"Error building last page: {exc}")
            last_page = ""
        try:
            tabs_content = f"""
            <div class="">                       
                {self.tabs.as_html(*args, **kwargs)}
            </div>
        """
        except Exception as exc:
            logger.error(f"Error building tabs content: {exc}")
            tabs_content = ""
        try:
            glossary_items = " ".join(
                [f"<li>{k}: {v}</li>" for k, v in self.glossary.items()]) if self.glossary is not None else ""
        except Exception as exc:
            logger.error(f"Error building glossary items: {exc}")
            glossary_items = ""

        glossary = f"""
               <section>
                   <div class="glossary">
                       <h2>Glossary</h2>
                       <p>This report was generated on {current_date}. </p>
                    {glossary_items} 
                   </div>
               </section>
               """
        body = f"""
            <div class="">
                {cover}
                <div class="">
                    {tabs_content}
                    {glossary if self.include_glossary else ""}
                    {last_page}
                </div>
            </div>
        """

        doc = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{self.title}</title>
            </head>
            <body>
                {body}
            </body>
        </html>
        """
        logger.debug("DOC GENERATED...")
        return doc


    @inspect_pdf
    def as_pdf(self, save_to_tmp: bool = False, *args, **kwargs) -> tuple[Union[Path, BytesIO], str]:
        logger.info(f"""
                    OCEAN REPORT AS PDF
                    --------------------------------
                    {kwargs=}
                    """
                    )
        try:
            if kwargs.get("read_firestore", True):
                self.read_configuration_from_firestore(*args, **kwargs)
        except NotFoundException as exc:
            logger.error(f"Error building self: {exc}")
            raise exc

        kwargs.update(
            **{
                "agency_name": self.agency_name,
                "configuration_id": self.configuration_id,
                "date_start": kwargs.get("date_start", None) or self.date_start,
                "date_end": kwargs.get("date_end", None) or self.date_end,
                "report_context": kwargs.get("report_context", ReportContext()) ,
            }
        )
        try:

            stylesheets = []
            try:
                css_base_path = Path() / "static" / "css"
                if not css_base_path.exists():
                    css_base_path = Path() / "ocean_reports" / "static" / "css"
                for css_file in self.css_files:
                    stylesheets.append(CSS(string=(css_base_path / css_file).read_text()))

            except Exception as exc:
                logger.error(f"Error loading custom CSS: {exc}")

            f_name = self.build_pdf_name(*args, **kwargs)

            try:
                report_html = HTML(string=self.as_html(*args, **kwargs))

                report_html.metadata = {
                    "Title": self.title,
                    "Author": "Ocean.Team@Sabre.com",
                    "Subject": "Report",
                    "Keywords": "KPI, Report, Ocean, Sabre",
                    'CreationDate': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            except Exception as exc:
                logger.error(f"Error creating HTML: {exc}")
                raise Exception(f"Error creating HTML: {exc}")
            if save_to_tmp:
                try:
                    f_name = "TEMP_pfd.PDF"
                    pdf_path = Path() / "tmp" / "pdfs"
                    pdf_path.mkdir(parents=True, exist_ok=True)
                    out_path = pdf_path / f_name

                    report_html.write_pdf(out_path, stylesheets=stylesheets)
                    print(f'{out_path=}')
                    return out_path, f_name
                except Exception as exc:
                    logger.error(f"Error saving PDF to tmp: {exc}")
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
                    logger.error(f"Error creating PDF buffer: {exc}")
                    raise Exception(f"Error creating PDF buffer: {exc}")
        except Exception as exc:
            logger.error(f"Error creating PDF: {exc}")
            raise Exception(f"Error creating PDF: {exc=}")

    def build_pdf_name(self, *args, **kwargs) -> str:
        try:
            configuration_id = kwargs.get("configuration_id", None)
            assert configuration_id is not None, "configuration_id is required"

        except Exception as exc:
            logger.error(f"Error building PDF name: {exc}")
            return None
        return f"{configuration_id}.pdf"

    def send_pdf_to_gcs(self, *args, **kwargs) -> str:
        try:
            logger.debug(f"""
               VBP REPORT SEND PDF TO GCS
               ---------------------------
               """)

            out_path, f_name = self.as_pdf(*args, **kwargs)

            return upload_blob(
                bucket_name=settings.gcp.bucket_name,
                source_file=out_path,
                destination_blob_name=f"extra_attachments/{f_name}"
            )
        except Exception as exc:
            logger.error(f"Error sending PDF to GCS: {exc}")
            return ""

    def get_executive_summary(self, *args, **kwargs):  # TODO: not implemented, but could be a good optional add on

        return f"""
        Report run on {datetime.today().strftime("%d-%m-%Y")} for {self.agency_name} from {self.date_start} to {self.date_end}.

        """
        ...

    def build_cover(self, *args, **kwargs):
        today = datetime.today()
        current_date = today.strftime(DATE_FORMAT)
        agency_name = kwargs.get("agency_name", None)
        date_start = kwargs.get("date_start", None)
        date_end = kwargs.get("date_end", None)
        img_path = Path() / "static" / "img"
        # Removed for file size: <img src="{cover_img}" alt="" class="cover-image">

        if not img_path.exists():
            img_path = Path() / "ocean_reports" / "static" / "img"

        with open(img_path / "sabre_logo.txt") as f:
            sabre_logo_str = f.read()

        return f"""
                  <div class="cover">
                      <div class="container">
                      <div class="cover-header">
                          <div class="title">{self.title}</div>
                              <div class="report-details">Name: {agency_name}</div>      
                              <div class="report-details">Generated on: {current_date}</div>      
                              <div class="report-details">Report date: {date_start} to {date_end}</div>      
                          </div>                    
                          <img src="{sabre_logo_str}" alt="Sabre" class="logo">
                      </div>                    
                  </div>
              """


class ReportTemplate(Report):
    @model_validator(mode="after")
    def build_self(self) -> "ReportTemplate":
        return self

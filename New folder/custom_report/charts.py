"""
This module contains the chart methods for the VBP report.
"""
import logging
from typing import List

import pandas as pd

from helpers import filter_df_by_top, split_df
from schemas.components import response_time_buckets
from schemas.custom_report.chartcomponent import ChartComponent, ChartTrace, ChartTraceType, MAIN_PALETTE
from schemas.data_sources.data_sources_handler import get_df_from_ds
from schemas.kpi_report.stats import process_l2b_data_by_date
from schemas.kpi_report.tables import bookability_aggregations, _get_failure_rate

logger = logging.getLogger(__name__)

DEC_FORMAT = ",.0f"
PERC_FORMAT = ".0%"
# # # #
# Bookability CHARTS
# # # #
micro_chart_width = 4

bookability_traces = [
    ChartTrace(
        mode="stack",
        name="Failure",
        type=ChartTraceType.BAR,
        y="sell_sessions_with_failure",
    ),
    ChartTrace(
        mode="stack",
        name="Success",
        type=ChartTraceType.BAR,
        y="number_of_sessions_with_success",
    ),
    ChartTrace(
        name="Failure Rate",
        secondary=True,
        type=ChartTraceType.LINE,
        y="failure_rate",
    )
]

empty_responses_traces = [

    ChartTrace(
        line_width=micro_chart_width,
        name="Percentage (%)",
        type=ChartTraceType.LINE,
        y="empty_responses_percent",
        secondary=True,

    ),
    ChartTrace(
        line_width=micro_chart_width,
        name="Empty Responses",
        opacity=0.5,
        type=ChartTraceType.BAR,
        y="empty_responses",
    ),
]

bookability_axes = {
    "x_axis": {"type": "date"},

    "y_axis1": {
        "title": "Sell Attempts",
    },
    "y_axis2": {
        "range": [0, 1],
        "title": "Failure Rate",
        "tickformat": PERC_FORMAT,
    },
}
range_mode_to_zero = "tozero"

l2b_axis_secondary = {
    "title": "L2B",
    "rangemode": "tozero",
    # "tickformat": lambda x: human_readable(x, 0),
}
shopping_requests_axis = {
    "title": "Shopping Requests",
}

RT_COLORS = [
    "#D0E1F9",  # Lightest Blue
    "#A9C4EB",
    "#84A7DE",
    "#5F8BD1",
    "#3A70C4",
    "#1957B7",
    "#0D439A",
    "#022E7A"  # Darkest Blue
]

l2b_traces = [
    ChartTrace(y="l2b_rq", name="Requests", opacity=0.5, type=ChartTraceType.BAR),
    ChartTrace(y="l2b", name="L2B", type=ChartTraceType.LINE, secondary=True),
]

response_time_buckets_traces = [
    # ChartTrace(y="avg_response_time", name="Average RT", type=ChartTraceType.BAR, secondary=True, opacity=0.8,
    #            color="#a9a9b5"),
    # ChartTrace(y="resp_time_above_5s", name=">5s", type=ChartTraceType.AREA, color=RT_COLORS[0]),
    ChartTrace(y="resp_time_below_5s", name="<5s", type=ChartTraceType.AREA, color=RT_COLORS[6], custom_text="<5s",
               mode="lines+markers+text"),
    ChartTrace(y="resp_time_below_3s", name="<3s", type=ChartTraceType.AREA, color=RT_COLORS[5], custom_text="<3s",
               mode="lines+markers+text"),
    ChartTrace(y="resp_time_below_2s", name="<2s", type=ChartTraceType.AREA, color=RT_COLORS[4], custom_text="<2s",
               mode="lines+markers+text"),
    ChartTrace(y="resp_time_below_1s", name="<1s", type=ChartTraceType.AREA, color=RT_COLORS[3], custom_text="<1s",
               mode="lines+markers+text"),
    ChartTrace(y="resp_time_below_500ms", name="<500ms", type=ChartTraceType.AREA, color=RT_COLORS[2],
               custom_text="<500ms", mode="lines+markers+text"),
    ChartTrace(y="resp_time_below_250ms", name="<250ms", type=ChartTraceType.AREA, color=RT_COLORS[1],
               custom_text="<250ms", mode="lines+markers+text"),
    ChartTrace(y="resp_time_below_100ms", name="<100ms", type=ChartTraceType.AREA, color=RT_COLORS[0],
               custom_text="<100ms", mode="lines+markers+text"),
]


class BookabilityCharts:

    def process_bookability_data(df, *args, **kwargs) -> pd.DataFrame:
        """
        Processes a DataFrame of bookability data.

        Args:
            df (pd.DataFrame): The DataFrame to process.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. Expects 'filter_on', 'filter_by', 'top_x', 'group_by', and 'aggregations'.

        Returns:
            pd.DataFrame: The processed DataFrame.

        Raises:
            Exception: If there is an error in processing the DataFrame, an exception is raised.
        """
        try:
            # Get the filter parameters from the keyword arguments
            filter_on = kwargs.get("filter_on", None)
            filter_by = kwargs.get("filter_by", None)
            top_x = kwargs.get("top_x", 6)

            # If a filter is specified, apply the filter to the DataFrame
            if filter_on is not None:
                df = filter_df_by_top(df, on=filter_on, by=filter_by, top_x=top_x)

            # Get the group by parameters from the keyword arguments
            group_by = kwargs.get("group_by", ["date"])
            aggregations = kwargs.get("aggregations", bookability_aggregations)

            # Group the DataFrame by the specified columns and perform the specified aggregations
            df = df.groupby(group_by).agg(aggregations).reset_index()

            # Calculate the failure rate and the number of sessions with success
            _get_failure_rate(df)
            df["number_of_sessions_with_success"] = df["sell_sessions"] - df["sell_sessions_with_failure"]
            df.set_index("date", inplace=True)

            return df
        except Exception as e:
            # Log the error and raise the exception
            logger.error(f"Error processing bookability data: {e}")
            logger.error(df.columns)
            raise e

    def by_date(*args, **kwargs) -> List[ChartComponent]:
        """Returns the Line Chart For Failure Rate per date, and the average line of the failure rate.
        """

        @get_df_from_ds(ds_key="bookability")
        def _method_bookability_by_date(df: pd.DataFrame, *args, **kwargs):
            return BookabilityCharts.process_bookability_data(df, *args, **kwargs)

        return [
            ChartComponent(
                bar_mode="stack",
                description="""
                Request Count Daily. Shopping request count by day.
                        Split by standard BFM 200 request count and Total""",
                method=_method_bookability_by_date,
                title="Bookability by Date",
                traces=bookability_traces,
                type="combo",
                uid="kpi-chart-bookability-by-date",
                **bookability_axes
            )
        ]

    def by_date_new(*args, **kwargs) -> List[ChartComponent]:
        """Returns the Line Chart For Failure Rate per date, and the average line of the failure rate.
        """

        @get_df_from_ds(ds_key="bookability")
        def _method_bookability_by_date(df: pd.DataFrame, *args, **kwargs):
            return BookabilityCharts.process_bookability_data(df, *args, **kwargs)

        return [
            ChartComponent(
                method=_method_bookability_by_date,
                traces=bookability_traces,

                uid="kpi-chart-bookability-by-date",
                **bookability_axes
            )  # .as_dash(*args, **kwargs)
        ]

    def failure_rate_by_date(*args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="bookability")
        def _method_failure_rate_by_date(df: pd.DataFrame, *args, **kwargs):
            return BookabilityCharts.process_bookability_data(df, *args, **kwargs)

        return [
            ChartComponent(
                bar_mode="stack",
                description="""Shows booking failure rate figures by date.""",
                method=_method_failure_rate_by_date,
                title="Failure Rate by Date",
                traces=[
                    ChartTrace(
                        color=MAIN_PALETTE[0],
                        line_width=micro_chart_width,
                        name="Failure Rate",
                        type=ChartTraceType.LINE,
                        y="failure_rate",
                    )

                ],
                type="combo",
                uid="kpi-chart-failure-rate-by-date",
                x_axis={"type": "date"},
                y_axis1={
                    "rangemode": range_mode_to_zero,
                    "title": "Failure Rate",
                    "tickformat": PERC_FORMAT,
                },
            )
        ]

    @get_df_from_ds(ds_key="bookability")
    def by_date_per_pcc(df: pd.DataFrame, *args, **kwargs) -> List[ChartComponent]:
        split_by = "pcc"
        top_x_by_col = "sell_sessions"
        top_x = 6
        df = BookabilityCharts.process_bookability_data(
            df,
            group_by=["date", "pcc"],
            filter_on=split_by,
            filter_by=top_x_by_col,
            top_x=top_x,
            *args, **kwargs
        )

        split_dfs = split_df(df, by=split_by)

        return [
            ChartComponent(
                bar_mode="stack",
                df=_df,
                title=f"Bookability for {pcc}",
                traces=bookability_traces,
                uid=f"kpi-chart-bookability-by-date-for-{pcc}",
                type="combo",
                **bookability_axes
            )
            for pcc, _df in split_dfs.items()
        ]

    @get_df_from_ds(ds_key="bookability")
    def by_date_per_airline(df: pd.DataFrame, *args, **kwargs) -> List[ChartComponent]:
        split_by = "airline"
        top_x_by_col = "sell_sessions"
        top_x = 6

        df = BookabilityCharts.process_bookability_data(
            df,
            group_by=["date", "airline"],
            filter_on=split_by,
            filter_by=top_x_by_col,
            top_x=top_x,
            *args, **kwargs
        )
        split_dfs = split_df(df, by=split_by, order_by=top_x_by_col)

        return [
            ChartComponent(
                bar_mode="stack",
                df=_df,
                title=f"Bookability  for {airline}",
                traces=bookability_traces,
                uid=f"kpi-chart-bookability-by-date-for-{airline}",
                type="combo",

                **bookability_axes
            )
            for airline, _df in split_dfs.items()
        ]


class L2BCharts:
    @classmethod
    def post_processor(cls, df, *args, **kwargs):
        ...
        return df

    @classmethod
    def by_date(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_by_date(df: pd.DataFrame, *args, **kwargs):
            _df = process_l2b_data_by_date(df)
            _df.set_index("date", inplace=True)
            return _df

        return [
            ChartComponent(
                bar_mode="stack",
                description="""Shows Look to Book by Date""",
                method=_method_by_date,
                title="L2B by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="L2B",
                        type=ChartTraceType.LINE,
                        y="l2b",

                    )
                ],
                type="combo",
                uid="kpi-chart-bookability",
                x_axis={"type": "date"},
                y_axis1={"title": "L2B", "rangemode": range_mode_to_zero},
            )]

    @classmethod
    def rqs_and_l2b_by_date(cls, *args, **kwargs) -> List[ChartComponent]:
        """Bar Chart for the number of shopping requests
        Line chart for the L2B.
        """

        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_rqs_and_l2b(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            _df = process_l2b_data_by_date(df)
            _df.set_index("date", inplace=True)
            return _df

        return [
            ChartComponent(
                method=_method_rqs_and_l2b,
                title="Requests and L2B by Date",
                traces=l2b_traces,
                type="combo",
                uid="chart-rqs-and-l2b-by-date",
                x_axis={"type": "date"},
                # x_label="date",
                y_axis1=shopping_requests_axis,
                y_axis2=l2b_axis_secondary

            )
        ]

    @classmethod
    def shopping_requests_by_date(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_shopping_requests_by_date(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            _df = process_l2b_data_by_date(df)
            _df.set_index("date", inplace=True)
            return _df

        return [
            ChartComponent(
                method=_method_shopping_requests_by_date,
                title="Shops by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="Requests",
                        type=ChartTraceType.LINE,
                        y="requests",
                    )
                ],
                type="combo",
                uid="chart-shopping-requests-by-date",
                x_axis={"type": "date"},
                x_label="date",
                y_axis1=shopping_requests_axis,

            )
        ]

    @classmethod
    def shopping_requests_by_date_with_title(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_shopping_requests_by_date(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            _df = process_l2b_data_by_date(df)
            _df.set_index("date", inplace=True)
            return _df

        return [
            ChartComponent(
                method=_method_shopping_requests_by_date,
                title="Shopping Requests by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="Requests",
                        type=ChartTraceType.BAR,
                        y="requests",
                    )
                ],
                type="combo",
                uid="chart-shopping-requests-by-date",
                x_axis={"type": "date"},
                x_label="date",
                y_axis1=shopping_requests_axis,

            )
        ]

    @classmethod
    def bookings_by_date(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_bookings_by_date(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            _df = process_l2b_data_by_date(df)
            _df.set_index("date", inplace=True)
            return _df

        return [
            ChartComponent(
                method=_method_bookings_by_date,
                title="Bookings by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="Bookings",
                        type=ChartTraceType.LINE,
                        y="bookings",
                    )

                ],
                type="combo",
                uid="chart-bookings-by-date",
                x_axis={"type": "date"},
                x_label="date",
                y_axis1={"title": "Bookings", "tickformat": DEC_FORMAT},
            )
        ]

    @classmethod
    def bookings_by_date_with_title(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_bookings_by_date(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            _df = process_l2b_data_by_date(df)
            _df.set_index("date", inplace=True)
            return _df

        return [
            ChartComponent(
                method=_method_bookings_by_date,
                title="Bookings by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="Bookings",
                        type=ChartTraceType.BAR,
                        y="bookings",
                    )

                ],
                type="combo",
                uid="chart-bookings-by-date",
                x_axis={"type": "date"},
                x_label="date",
                y_axis1={
                    "rangemode": range_mode_to_zero,
                    "title": "Bookings",
                },
            )
        ]

    @classmethod
    def l2b_by_date_per_pcc(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_by_date_per_pcc(df: pd.DataFrame, *args, **kwargs):
            split_by = "pcc"
            group_by = ["date"]
            gb = [split_by] + group_by if group_by is not None else [split_by]
            top_x_by_col = "bookings"
            aggregations = {"bookings": "sum", "l2b_rq": "sum"}
            dfg = df.groupby(gb).agg(aggregations).reset_index()
            dfg["l2b"] = dfg["l2b_rq"] / dfg["bookings"]
            top_x = 6

            filtered_df = filter_df_by_top(dfg, on=split_by, by=top_x_by_col, top_x=top_x)
            split_dfs = split_df(filtered_df, by=split_by)

            dfg_total = dfg.groupby(group_by).agg(aggregations).reset_index()
            dfg_total["l2b"] = dfg_total["l2b_rq"] / dfg_total["bookings"]

            return [
                ChartComponent(
                    uid=f"kpi-chart-l2b-by-date-for-{pcc}",
                    title=f"L2B for {pcc}",
                    df=_df.set_index("date"),
                    traces=l2b_traces,
                    type="combo",
                    x_axis={"type": "date"},
                    y_axis1=shopping_requests_axis,
                    y_axis2=l2b_axis_secondary,
                )
                for pcc, _df in split_dfs.items()
            ]

        return _method_by_date_per_pcc(*args, **kwargs)

    @classmethod
    def number_of_itineraries(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=cls.post_processor)
        def _method_number_of_itins(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            _df = process_l2b_data_by_date(df)
            _df.set_index("date", inplace=True)
            return _df

        return [
            ChartComponent(
                method=_method_number_of_itins,
                # title="Number of Itineraries by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="Itineraries",
                        type=ChartTraceType.LINE,
                        y="average_number_of_itineraries",
                    )
                ],
                type="combo",
                uid="chart-number-of-itineraries",
                x_axis={"type": "date"},
                # x_label="date",
                y_axis1={
                    "rangemode": range_mode_to_zero,
                    "tickformat": DEC_FORMAT,
                    "title": "Itineraries",
                },
            )
        ]


class ServicesCharts:

    @classmethod
    def post_processor(cls, df, *args, **kwargs):
        df = df[
            df["invoked_service"].str.startswith("BargainFinderMax") |
            df["invoked_service"].isin(["RevalidateItinRQ"])
            ]
        return df

    @classmethod
    def number_of_itins_per_date__service(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="services", fill_na=0, post_processor=cls.post_processor)
        def _method(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            group_by = ["date", "invoked_service"]
            aggregations = {
                "requests": "sum",
                "returned_itineraries": "sum"
            }

            df = df.fillna(0).infer_objects(copy=False)

            dfg = df.groupby(group_by).agg(aggregations).reset_index()

            dfg["average_number_of_itineraries"] = dfg["returned_itineraries"] / dfg["requests"]
            dfg = dfg.pivot(
                index="date",
                columns="invoked_service",
                values=["average_number_of_itineraries"]
            ).reset_index()
            dfg.set_index("date", inplace=True)
            return dfg['average_number_of_itineraries']

        dfg = _method(*args, **kwargs)

        services = dfg.columns

        traces = [
            ChartTrace(
                name=service,
                type=ChartTraceType.LINE,
                y=service,
            )
            for service in services
        ]

        return [
            ChartComponent(
                method=_method,
                traces=traces,
                type="combo",
                uid="chart-number-of-itineraries",
                x_axis={"type": "date"},
                x_label="date",
                y_axis1={
                    "rangemode": range_mode_to_zero,
                    "tickformat": DEC_FORMAT,
                    "title": "Itineraries",
                },
            )
        ]


class ResponseTimeCharts:
    @classmethod
    def post_processor(cls, df, *args, **kwargs):
        df = df[
            df["invoked_service"].str.startswith("BargainFinderMax") |
            df["invoked_service"].isin(["RevalidateItinRQ"])
            ]
        return df

    @classmethod
    def by_date(cls, *args, **kwargs) -> List[ChartComponent]:

        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=None)
        def _method_response_time_by_date(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            print(df.columns)
            group_by = ["date"]
            aggregations = {
                "response_time": "sum",
                "l2b_rq": "sum",
                "requests": "sum",
            }

            df = df.fillna(0).infer_objects(copy=False)

            dfg = df.groupby(group_by).agg(aggregations).reset_index()

            dfg["avg_response_time"] = dfg["response_time"] / dfg["l2b_rq"]
            dfg.set_index("date", inplace=True)
            return dfg

        return [
            ChartComponent(
                uid="kpi-chart-response-time-date",
                method=_method_response_time_by_date,
                title="Resp. Time by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="Average RT",
                        opacity=0.8,
                        type=ChartTraceType.LINE,
                        y="avg_response_time",
                    ),
                ],
                type="combo",
                x_axis={"type": "date"},
                y_axis1={
                    "rangemode": range_mode_to_zero,
                    "title": "Avg Response Time (s)"
                },
            )
        ]

    @classmethod
    def count_by_bucket__date(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="l2b", fill_na=0, post_processor=None)
        def _method_response_time_count_by_bucket_and_date(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            group_by = ["date"]
            aggregations = {
                "l2b_rq": "sum", "response_time": "sum"
            }

            df = df.fillna(0).infer_objects(copy=False)

            aggregations.update({bucket: "sum" for bucket in response_time_buckets if bucket in df.columns})

            dfg = df.groupby(group_by).agg(aggregations).reset_index()

            dfg["avg_response_time"] = dfg["response_time"] / dfg["l2b_rq"]
            dfg["requests"] = dfg["l2b_rq"]

            for bucket in response_time_buckets:
                if bucket in dfg.columns:
                    try:
                        dfg[bucket] = dfg[bucket] / dfg["requests"]
                    except Exception as exc:
                        print(f"Error processing {bucket}")
                        print(f"Error processing {exc=}")

            dfg.set_index("date", inplace=True)

            return dfg

        return [
            ChartComponent(
                hover_mode="x",
                method=_method_response_time_count_by_bucket_and_date,
                title="Response Time by Bucket and Date",
                traces=response_time_buckets_traces,
                type="combo",
                uid="kpi-chart-response-time-by-bucket-and-date",
                x_axis={"type": "date"},
                x_column="date",
                x_label="date",
                y_axis1={"title": "% of Requests", "tickformat": PERC_FORMAT, "range": [0, 1]},
                yaxis_range=[0, 1],
                tickformat=PERC_FORMAT,
            )
        ]

    @classmethod
    def by_date__bucket_per_service(cls, *args, **kwargs) -> List[ChartComponent]:
        @get_df_from_ds(ds_key="services", fill_na=0, post_processor=cls.post_processor)
        def _method_response_time_count_by_bucket___date_per_service(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            group_by = ["date", "invoked_service"]
            aggregations = {
                "requests": "sum", "response_time": "sum"
            }

            df = df.fillna(0).infer_objects(copy=False)

            aggregations.update({bucket: "sum" for bucket in response_time_buckets if bucket in df.columns})

            dfg = df.groupby(group_by).agg(aggregations).reset_index()

            dfg["avg_response_time"] = dfg["response_time"] / dfg["requests"]

            for bucket in response_time_buckets:
                if bucket in dfg.columns:
                    try:
                        dfg[bucket] = dfg[bucket] / dfg["requests"]
                    except Exception as exc:
                        print(f"Error processing {bucket}")
                        print(f"Error processing {exc=}")

            dfg.set_index("date", inplace=True)
            return dfg

        split_by = "invoked_service"
        group_by = ["date"]

        df = _method_response_time_count_by_bucket___date_per_service(*args, **kwargs)
        top_x_by_col = "requests"

        top_x = 6
        filtered_df = filter_df_by_top(df, on=split_by, by=top_x_by_col, top_x=top_x)
        split_dfs = split_df(filtered_df, by=split_by)

        return [
            ChartComponent(
                df=_df,
                title=f"{svc}",
                traces=response_time_buckets_traces,
                type="combo",
                uid=f"kpi-chart-response-time-by-date--bucket-for-{svc}",
                x_axis={"type": "date"},
                x_column="date",
                x_label="date",
                y_axis1={"title": "% of Requests", "tickformat": PERC_FORMAT, "range": [0, 1]},
                y_axis2={"title": "Avg Response Time (s)"},

            )
            for svc, _df in split_dfs.items()
        ]


class EmptyResponsesCharts:
    @classmethod
    def post_processor(cls, df, *args, **kwargs):
        df = df[
            df["invoked_service"].str.startswith("BargainFinderMax") |
            df["invoked_service"].isin(["RevalidateItinRQ"])
            ]
        return df

    @classmethod
    def by_date(cls, *args, **kwargs):
        """Bar chart for number of empty responses per date.
        also line chart for the percentage of empty responses.
        """

        @get_df_from_ds(ds_key="services", fill_na=0, post_processor=cls.post_processor)
        def _method_empty_responses_trend(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            logger.debug(f"""
            Calling _method_empty_responses_trend
            -------------------------------------
            """)
            _df = process_l2b_data_by_date(df)

            _df["date"] = _df["date"].astype(str)
            _df.set_index("date", inplace=True)

            return _df

        return [
            ChartComponent(
                description="""Empty Responses by Date""",
                method=_method_empty_responses_trend,
                title="Empty Resp. by Date",
                traces=[
                    ChartTrace(
                        line_width=micro_chart_width,
                        name="Percentage (%)",
                        type=ChartTraceType.LINE,
                        y="empty_responses_percent",
                    ),
                ],
                type="combo",
                uid="chart-empty-responses-by-date",
                x_axis={"type": "date"},
                y_axis1={"title": "Empty Responses %", "tickformat": PERC_FORMAT, "range": [0, 1]},
            )
        ]

    @classmethod
    def by_date_per_pcc(cls, *args, **kwargs):
        @get_df_from_ds(ds_key="services", fill_na=0, post_processor=cls.post_processor)
        def _method_empty_responses_by_date_per_pcc(df: pd.DataFrame, *args, **kwargs):
            _df = process_l2b_data_by_date(df, group_by=["date", "pcc"])
            _df["date"] = _df["date"].astype(str)
            _df.set_index("date", inplace=True)
            return _df

        split_by = "pcc"
        top_x_by_col = "requests"
        top_x = 6

        df = _method_empty_responses_by_date_per_pcc(*args, **kwargs)

        filtered_df = filter_df_by_top(df, on=split_by, by=top_x_by_col, top_x=top_x)
        split_dfs = split_df(filtered_df, by=split_by)

        return [
            ChartComponent(
                df=_df,
                title=f"{pcc}",
                traces=empty_responses_traces,
                type="combo",
                uid=f"kpi-chart-empty-responses-by-date-for-{pcc}",
                x_axis={"type": "date"},
                x_column="date",
                x_label="date",
                y_axis1={"title": "Empty Responses", },
                y_axis2={"title": "Empty Responses %", "tickformat": PERC_FORMAT, "range": [0, 1]},

            )
            for pcc, _df in split_dfs.items()
        ]

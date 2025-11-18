"""
CardComponents used for KPI Report
"""

from schemas.components.ui_base_component import UIBaseComponent
from schemas.custom_report import CardComponent, RowComponent
from schemas.custom_report.charts import BookabilityCharts, L2BCharts, EmptyResponsesCharts, ResponseTimeCharts, \
    ServicesCharts
# from schemas.kpi_report.stats import stat_failure_rate, stat_response_time, stat_failure_rate_target, \
#     response_time_target, stat_l2b, stat_l2b_target, stat_empty_responses_percent, stats_empty_responses_target, \
#     stat_avg_requests, stat_avg_bookings, stat_number_of_itineraries, stat_ota_empty_responses_percent
# from schemas.kpi_report.tables import BookabilityTables, L2BTables, ResponseTimeTables, EmptyResponsesTables

stat_layout = ""
distribute_content_default = "col-xs-12 col-sm-6 col-md-6 col-lg-6 col-kpi-6"

class Cards:
    class Chart:
        class FailureRate:
            by_date = CardComponent(
                layout="col-6",
                method=BookabilityCharts.by_date,
                uid="kpi-card-chart-bookability-by-date",

            )

            failure_rate_by_date = CardComponent(
                layout="col-6",
                method=BookabilityCharts.failure_rate_by_date,
                uid="kpi-card-chart-bookability-failure-rate-by-date",
            )
            by_date_per_airline = CardComponent(
                method=BookabilityCharts.by_date_per_airline,
                uid="kpi-card-chart-bookability-by-date-per-airline",
            )
            by_date_per_pcc = RowComponent(
                distribute_content=distribute_content_default,
                method=BookabilityCharts.by_date_per_pcc,
                uid="kpi-card-chart-bookability-by-date-per-pcc",
            )

        class ShoppingRequests:
            by_date = CardComponent(
                layout="col-6",
                method=L2BCharts.shopping_requests_by_date,
                uid="kpi-cardComponent-chart-shopping-requests",
            )
            by_date_with_title = CardComponent(
                layout="col-6",
                method=L2BCharts.shopping_requests_by_date_with_title,
                uid="kpi-cardComponent-chart-shopping-requests",
            )

        class L2B:
            by_date = CardComponent(
                method=L2BCharts.by_date,
                uid="kpi-cardComponent-chart-l2b",
            )
            rqs_and_l2b = CardComponent(
                method=L2BCharts.rqs_and_l2b_by_date,
                uid="kpi-cardComponent-chart_rqs_and_l2b",
            )
            l2b_by_date_per_pcc = RowComponent(
                distribute_content=distribute_content_default,
                method=L2BCharts.l2b_by_date_per_pcc,
            )
            bookings_by_date = CardComponent(
                method=BookabilityCharts.by_date,
                uid="kpi-cardComponent-chart-bookings-by-date",
            )
            bookings_by_date_with_title = CardComponent(
                method=L2BCharts.bookings_by_date_with_title,
                uid="kpi-cardComponent-chart-bookings-by-date",
            )
            number_of_itineraries = CardComponent(
                method=L2BCharts.number_of_itineraries,
                uid="kpi-cardComponent-chart-number-of-itineraries",
            )

        class EmptyResponses:
            by_date_per_pcc = RowComponent(
                distribute_content=distribute_content_default,
                method=EmptyResponsesCharts.by_date_per_pcc,
                uid="kpi-cardComponent-chart-empty-responses-by-pcc--date",
            )
            by_date = CardComponent(
                method=EmptyResponsesCharts.by_date,
                uid="kpi-cardComponent-chart-empty-responses",
            )

        class ResponseTime:
            by_date = CardComponent(
                method=ResponseTimeCharts.by_date,
                uid="kpi-cardComponent-chart-response-time-count-by-bucket--date",
            )
            count_by_bucket__date = CardComponent(
                method=ResponseTimeCharts.count_by_bucket__date,
                uid="kpi-cardComponent-chart-response-time-count-by-bucket--date",
            )
            by_date__bucket_per_service = RowComponent(
                distribute_content=distribute_content_default,
                method=ResponseTimeCharts.by_date__bucket_per_service,
                uid="kpi-cardComponent-chart-response-time-count-by-bucket--date",
            )

        class Services:
            number_of_itins_per_date__service = CardComponent(
                method=ServicesCharts.number_of_itins_per_date__service,
                uid="kpi-cardComponent-chart-number-of-itineraries",
            )

    # class Table:
    #     class FailureRate:
    #         by_pcc = CardComponent(
    #             method=BookabilityTables.by_pcc,
    #             uid="kpi-cardComponent-table-bookability-by-pcc",
    #         )
    #         by_airline = CardComponent(
    #             method=BookabilityTables.by_airline,
    #             uid="kpi-cardComponent-table-bookability-by-airline",
    #         )
    #         by_airline__pcc = CardComponent(
    #             method=BookabilityTables.by_airline__pcc,
    #             uid="kpi-cardComponent-table-bookability-by-airline--pcc",
    #         )
    #
    #     class L2B:
    #         by_week = CardComponent(
    #             method=L2BTables.by_week,
    #             uid="kpi-cardComponent-table-l2b-by-week",
    #         )
    #         by_pcc__week = CardComponent(
    #             method=L2BTables.by_pcc__week,
    #             uid="kpi-cardComponent-table-l2b-by-pcc--week",
    #         )
    #
    #     class ResponseTime:
    #         by_pcc__bucket = CardComponent(
    #             method=ResponseTimeTables.by_pcc__bucket,
    #             uid="kpi-cardComponent-table-response-time-by-pcc--bucket",
    #         )
    #         by_date__bucket = CardComponent(
    #             method=ResponseTimeTables.date__bucket,
    #             uid="kpi-cardComponent-table-response-time-by-date--bucket",
    #         )
    #
    #     class EmptyResponses:
    #         by_invoked_service = CardComponent(
    #             method=EmptyResponsesTables.by_invoked_service,
    #             uid="kpi-cardComponent-table-empty-responses-by-invoked-service",
    #         )
    #         by_pcc = CardComponent(
    #             method=EmptyResponsesTables.by_pcc,
    #             uid="kpi-cardComponent-table-empty-responses-by-pcc",
    #         )
    #         by_service = CardComponent(
    #             method=EmptyResponsesTables.by_invoked_service,
    #             uid="kpi-cardComponent-table-empty-responses-by-pcc",
    #         )
    #         by_pcc__invoked_service = CardComponent(
    #             method=EmptyResponsesTables.by_pcc__invoked_service,
    #             uid="kpi-cardComponent-table-empty-responses-by-pcc--invoked-service",
    #         )
    #         by_date = CardComponent(
    #             method=EmptyResponsesTables.by_date,
    #             uid="kpi-cardComponent-table-empty-responses-by-date",
    #         )
    #
    # class Stat:
    #     failure_rate = CardComponent(
    #         description="This is the failure rate",
    #         footer=UIBaseComponent(class_name="kpi-cardComponent-footer", method=stat_failure_rate_target),
    #         layout=stat_layout,
    #         method=stat_failure_rate,
    #         title="Failure Rate",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-failure-rate",
    #     )
    #     response_time = CardComponent(
    #         description="This is the Average Response Time Target",
    #         footer=UIBaseComponent(method=response_time_target),
    #         layout=stat_layout,
    #         method=stat_response_time,
    #         title="Response Time",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-response-time",
    #     )
    #     l2b = CardComponent(
    #         footer=UIBaseComponent(method=stat_l2b_target),
    #         layout=stat_layout,
    #         method=stat_l2b,
    #         title="Look to Book",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-l2b",
    #
    #     )
    #     l2b_wo_footer = CardComponent(
    #         uid="kpi-cardComponent-stat-l2b-wo-footer",
    #         footer=None,
    #         layout=stat_layout,
    #         method=stat_l2b,
    #         title="Look to Book",
    #         type="big-statistic",
    #
    #     )
    #     empty_responses = CardComponent(
    #         footer=UIBaseComponent(method=stats_empty_responses_target),
    #         layout=stat_layout,
    #         method=stat_empty_responses_percent,
    #         title="Empty Responses",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-empty-responses",
    #     )
    #     ota_empty_responses = CardComponent(
    #         footer=UIBaseComponent(method=stats_empty_responses_target),
    #         layout=stat_layout,
    #         method=stat_ota_empty_responses_percent,
    #         title="Empty Responses",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-empty-responses",
    #     )
    #     avg_requests = CardComponent(
    #         footer=UIBaseComponent(children="-"),
    #         layout=stat_layout,
    #         method=stat_avg_requests,
    #         title="Daily Shopping Requests",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-avg-requests",
    #
    #     )
    #     avg_bookings = CardComponent(
    #         footer=UIBaseComponent(children="-"),
    #         layout=stat_layout,
    #         method=stat_avg_bookings,
    #         title="Daily Bookings",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-avg-bookings",
    #
    #     )
    #     number_of_itins = CardComponent(
    #         footer=UIBaseComponent(children=["-"]),
    #         layout=stat_layout,
    #         method=stat_number_of_itineraries,
    #         title="Avg Number of Itins",
    #         type="big-statistic",
    #         uid="kpi-cardComponent-stat-number-of-itins",
    #
    #     )
#
# def test(*args, **kwargs):
#     cardComponent = CardComponents.Chart.FailureRate.by_date
#     return cardComponent.as_html(*args, **kwargs)


if __name__ == "__main__":
    kwargs = {
        # configuration_id=kpi--despegar-daily-kpi-report-beecc&date_start=2025-11-01&date_end=2025-11-01
        "configuration_id": "kpi--despegar-daily-kpi-report-beecc",
        "date_start": "2025-11-01",
        "date_end": "2025-11-01"

    }
    card = Cards.Chart.FailureRate.by_date_new
    print(card.as_html(**kwargs))


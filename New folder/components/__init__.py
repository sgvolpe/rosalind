from helpers import human_readable
from schemas.components.error import ErrorComponent

response_time_buckets = [
    "resp_time_below_100ms",
    "resp_time_below_250ms",
    "resp_time_below_500ms",
    "resp_time_below_1s",
    "resp_time_below_1ss",
    "resp_time_below_2s",
    "resp_time_below_3s",
    "resp_time_below_5s",
    "resp_time_above_5s",
    "resp_time_above_10s"
]

# Index of methods to format tables by column name.
table_formatting_methods = {
    # KPI Reports
    "Bookings": human_readable,
    "Requests": human_readable,
    "L2B": int,
    "above_10s": lambda x: human_readable(x, 0),
    "average_response_time": lambda x: round(x, 1),
    "average_rt": lambda x: human_readable(x, 1),
    "avg": lambda x: round(x, 1),
    "empty_responses": lambda x: human_readable(x, 0),
    "empty_responses_rate": lambda x: f"{round(x * 100, 1)}%",
    "failure_rate": lambda x: f"{round(x * 100, 1)}%",
    "l2b": lambda x: float(x),
    "l2b_rq": lambda x: human_readable(x, 0),
    "requests": lambda x: human_readable(x, 0),
    "response_time": lambda x: human_readable(x, 0),
    "sell_sessions": lambda x: human_readable(x, 0),
    "sell_sessions_with_failure": lambda x: human_readable(x, 0),
    "total_with_success": human_readable,

    # VBP Report
    "%_of_total_std_bfm200_rq": lambda x: f"{round(x * 100, 2)}%",
    "%rq": lambda x: f"{int(x * 100)}%",
    "%std_bfm200_rq": lambda x: f"{int(x * 100)}%",
    "actual_std_bfm_200_l2b": lambda x: f"{int(x):,}",
    "avg_std_bfm_200_rate": lambda x: f"{round(x, 2)}",
    "request_count": lambda x: human_readable(x, 2),
    "std_bfm_200_request_count": lambda x: human_readable(x, 2),
    "target_std_bfm_200_l2b": lambda x: f"{int(x):,}",
}

table_formatting_methods.update({
    bucket: lambda x: f"{round(x * 100, 1)}%" for bucket in response_time_buckets
})

from urllib.parse import parse_qs
from urllib.parse import unquote

from dash import callback, Output, Input, State, ALL, MATCH


@callback(
    Output("edit-btn", "children"),
    Output("add-tab-btn-div", "style"),
    Output({'type': 'add-component-btn', 'tab': ALL, 'row': ALL, 'col': ALL}, 'style'),
    Output({'type': 'component-dropdown', 'tab': ALL, 'row': ALL, 'col': ALL}, 'style'),
    Output({'type': 'add-col-btn', 'tab': ALL, 'row': ALL}, 'style'),
    Output({'type': 'add-row-btn', 'tab': ALL}, 'style'),
    Output({'type': 'tab', 'tab': ALL}, 'className'),
    Output({'type': 'remove-tab-btn', 'tab': ALL}, 'style'),
    Output("combined-report-form-container", 'style'),
    Output("empty-page-div", 'style'),

    Input("edit-btn", "n_clicks"),

    State("edit-btn", "children"),
    State({'type': 'add-component-btn', 'tab': ALL, 'row': ALL, 'col': ALL}, 'style'),
    State({'type': 'component-dropdown', 'tab': ALL, 'row': ALL, 'col': ALL}, 'style'),
    State({'type': 'add-col-btn', 'tab': ALL, 'row': ALL}, 'style'),
    State({'type': 'add-row-btn', 'tab': ALL}, 'style'),
    State({'type': 'tab', 'tab': ALL}, 'className'),
    State({'type': 'remove-tab-btn', 'tab': ALL}, 'style'),

    # State("edit-section", "style"),
    prevent_initial_call=True
)
def toggle_edit_section(
        n_clicks, current_children, add_component_btn_styles, components_dropdown_styles, add_col_btn_styles,
        add_row_btn_styles,
        current_tab_classes,
        remove_tab_btn_styles,

):
    print("... {{ CALLBACK_TOGGLE_EDIT_SECTION }} ... ")
    print(f'{current_children=}')
    if current_children == ["Edit"]:
        btn_children = ["Save"]
        style = {"display": "block"}
        add_tab_btn_style = style
        add_component_btn_styles = [style for _ in add_component_btn_styles]
        components_dropdown_styles = [style for _ in components_dropdown_styles]
        add_col_btn_styles = [style for _ in add_col_btn_styles]
        add_row_btn_styles = [style for _ in add_row_btn_styles]
        updated_classes = []
        for class_name in current_tab_classes:
            aux = class_name.split(" ")
            aux.append("parent-hover")
            aux.append("parent-col-hover")
            updated_classes.append(" ".join(list(set(aux))))
        remove_tab_btn_styles = [style for _ in remove_tab_btn_styles]
        combined_report_form_style = {"display": "block"}
        empty_page_div_style = {"display": "block"}

    else:
        btn_children = ["Edit"]
        style = {"display": "none"}
        add_tab_btn_style = style
        add_component_btn_styles = [style for _ in add_component_btn_styles]
        components_dropdown_styles = [style for _ in components_dropdown_styles]
        add_col_btn_styles = [style for _ in add_col_btn_styles]
        add_row_btn_styles = [style for _ in add_row_btn_styles]
        updated_classes = []


        for class_name in current_tab_classes:
            updated_classes.append((class_name or "").replace(
                "parent-hover", ""
            ).replace(
                "parent-col-hover", ""
            )
            )
        remove_tab_btn_styles = [style for _ in remove_tab_btn_styles]

        combined_report_form_style = {"display": "none"}
        empty_page_div_style = {"display": "none"}


    return (
        btn_children, add_tab_btn_style, add_component_btn_styles, components_dropdown_styles, add_col_btn_styles,
        add_row_btn_styles, updated_classes, remove_tab_btn_styles, combined_report_form_style, empty_page_div_style
    )


@callback(
    Output({"type": "chart-settings-btn", "index": ALL}, "style"),
    Output({"type": "data-table-div", "index": ALL}, "style"),
    Output({"type": "chart-table-btn", "index": ALL}, "style"),
    Input("show-all-settings-btn", "n_clicks"),
    Input({"type": "chart-settings-btn", "index": ALL}, "style"),
    Input({"type": "data-table-div", "index": ALL}, "style"),
    Input({"type": "chart-table-btn", "index": ALL}, "style"),

    prevent_initial_call=True
)
def toggle_all_settings(n_clicks, elements, elements2, chart_table_buttons):
    print("... {{ CALLBACK_TOGGLE_ALL_SETTINGS }} ... ")
    style = {"display": "block"} if n_clicks % 2 != 0 else {"display": "none"}
    return [style for _ in elements], [style for _ in elements2], [style for _ in chart_table_buttons]

@callback(
    Output({'type': 'chart-settings-div', 'index': MATCH}, 'is_open'),
    Input({'type': 'chart-settings-btn', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)
def toggle_settings(n_clicks):
    print("... {{ CALLBACK_TOGGLE_SETTINGS_DIV }} ... ")
    return n_clicks % 2 != 0

@callback(
    Output("charts_style_store", "data"),
    Input({"type": "axis-1-auto-range", "index": ALL}, "value"),
    Input({"type": "axis-1-range-mode", "index": ALL}, "value"),
    Input({"type": "axis-1-show-ticks", "index": ALL}, "value"),
    Input({"type": "axis-1-show-title", "index": ALL}, "value"),
    Input({"type": "axis-2-auto-range", "index": ALL}, "value"),
    Input({"type": "axis-2-range-mode", "index": ALL}, "value"),
    Input({"type": "axis-2-show-ticks", "index": ALL}, "value"),
    Input({"type": "axis-2-show-title", "index": ALL}, "value"),
    State("charts_style_store", "data"),
    State("template_id_store", "data"),
    State({'type': 'chart-switchable', 'index': ALL}, 'figure'),
    prevent_initial_call=True
)
def update_chart_styles_store(
        axis_1_auto_range,
        axis_1_range_mode,
        axis_1_show_ticks,
        axis_1_show_title,
        axis_2_auto_range,
        axis_2_range_mode,
        axis_2_show_ticks,
        axis_2_show_title,
        store,
        template_id,
        figures
):
    print("... {{ CALLBACK_UPDATE_CHART_STYLES_STORE }} ... ")
    # Initialize template_id entry in store if not present
    template_data = store.setdefault(
        template_id, {
            "axis_1_auto_range": [],
            "axis_1_range_mode": [],
            "axis_1_show_ticks": [],
            "axis_1_title": [],
            "axis_1_show_title": [],
            "axis_2_auto_range": [],
            "axis_2_range_mode": [],
            "axis_2_show_ticks": [],
            "axis_2_show_title": [],
            "axis_2_title": [],

        }
    )

    template_data["axis_1_auto_range"] = axis_1_auto_range
    template_data["axis_1_range_mode"] = axis_1_range_mode
    template_data["axis_1_show_ticks"] = axis_1_show_ticks
    template_data["axis_1_show_title"] = axis_1_show_title
    template_data["axis_2_auto_range"] = axis_2_auto_range
    template_data["axis_2_range_mode"] = axis_2_range_mode
    template_data["axis_2_show_ticks"] = axis_2_show_ticks
    template_data["axis_2_show_title"] = axis_2_show_title

    if len(template_data["axis_1_title"]) == 0:
        template_data["axis_1_title"] = [figure["layout"]["yaxis"].get("title", "") for figure in figures]
    if len(template_data["axis_2_title"]) == 0:
        template_data["axis_2_title"] = [figure["layout"]["yaxis2"].get("title", "") for figure in figures]
    return store

@callback(
    Output({"type": "chart-switchable", "index": ALL}, "figure"),
    Input({"type": "chart-switchable", "index": ALL}, "figure"),
    Input("charts_style_store", "data"),
    State("template_id_store", "data"),
    prevent_initial_call=True,
)
def read_charts_styles_store(figures, store, template_id):
    print("... {{ CALLBACK_READ_CHARTS_STYLES_STORE }} ... ")
    if template_id in store:
        template_data = store[template_id]

        axis_1_auto_range_list = template_data.get("axis_1_auto_range", [])
        axis_1_range_mode_list = template_data.get("axis_1_range_mode", [])
        axis_1_show_ticks_list = template_data.get("axis_1_show_ticks", [])
        axis_1_show_title_list = template_data.get("axis_1_show_title", [])
        axis_1_title_list = template_data.setdefault("axis_1_title", [])
        axis_2_auto_range_list = template_data.get("axis_2_auto_range", [])
        axis_2_range_mode_list = template_data.get("axis_2_range_mode", [])
        axis_2_show_ticks_list = template_data.get("axis_2_show_ticks", [])
        axis_2_show_title_list = template_data.get("axis_2_show_title", [])
        axis_2_title_list = template_data.setdefault("axis_2_title", [])

        if len(axis_1_title_list) < len(figures):
            axis_1_title_list.extend([""] * (len(figures) - len(axis_1_title_list)))
        if len(axis_2_title_list) < len(figures):
            axis_2_title_list.extend([""] * (len(figures) - len(axis_2_title_list)))

        for e, (
                figure,
                axis_1_auto_range,
                axis_1_range_mode,
                axis_1_show_ticks,
                axis_1_show_title,
                axis_1_title,
                axis_2_auto_range,
                axis_2_range_mode,
                axis_2_show_ticks,
                axis_2_show_title,
                axis_2_title
        ) in enumerate(
            zip(
                figures,
                axis_1_auto_range_list,
                axis_1_range_mode_list,
                axis_1_show_ticks_list,
                axis_1_show_title_list,
                axis_1_title_list,
                axis_2_auto_range_list,
                axis_2_range_mode_list,
                axis_2_show_ticks_list,
                axis_2_show_title_list,
                axis_2_title_list,

            )
        ):

            figure["layout"]["yaxis"]["autorange"] = bool(axis_1_auto_range)
            figure["layout"]["yaxis"]["rangemode"] = axis_1_range_mode
            figure["layout"]["yaxis"]["range"] = None if axis_1_auto_range else [0, 1]
            figure["layout"]["yaxis"]["showticks"] = bool(axis_1_show_ticks)
            figure["layout"]["yaxis"]["showtitle"] = bool(axis_1_show_title)

            figure["layout"]["yaxis2"]["autorange"] = bool(axis_2_auto_range)
            figure["layout"]["yaxis2"]["rangemode"] = axis_2_range_mode
            figure["layout"]["yaxis"]["range"] = None if axis_1_auto_range else [0, 1]
            figure["layout"]["yaxis2"]["showticks"] = bool(axis_2_show_ticks)
            figure["layout"]["yaxis2"]["showtitle"] = bool(axis_2_show_title)

            if axis_1_show_title:
                figure["layout"]["yaxis"]["title"] = axis_1_title
            else:
                figure["layout"]["yaxis"]["title"] = ""
            if axis_2_show_title:
                figure["layout"]["yaxis2"]["title"] = axis_2_title
            else:
                figure["layout"]["yaxis2"]["title"] = ""
    return figures

@callback(
    Output({'type': 'chart-table-div', 'index': MATCH}, 'is_open'),
    Input({'type': 'chart-table-btn', 'index': MATCH}, 'n_clicks'),
    prevent_initial_call=True
)
def toggle_chart_table_div(n_clicks):
    print("... {{ CALLBACK_TOGGLE_CHART_TABLE_DIV }} ... ")
    return n_clicks % 2 != 0

@callback(
    Output("debug-content", "style"),
    Output({"type": "component-debug", "index": ALL}, "style"),
    Input("debug_store", "data"),
    Input({"type": "component-debug", "index": ALL}, "value"),
    prevent_initial_call=False
)
def toggle_debug_visibility(debug, component_debug_list):
    print("... {{ CALLBACK_TOGGLE_DEBUG_VISIBILITY }} ... ")
    debug_div_style = {"display": "block"} if debug in [True, "true"] else {"display": "none"}
    return debug_div_style, [debug_div_style for _ in component_debug_list]

@callback(
    Output("configuration_id_store", "data"),
    Output("debug_store", "data"),
    Output("date_end_store", "data"),
    Output("date_start_store", "data"),
    Output("template_store", "data"),
    Input("url", "search"),
    Input("debug-btn", "n_clicks"),
    State("debug_store", "data"),

)
def url_into_store(search, debug_btn_clicks, current_debug_state):
    print("... {{ CALLBACK_URL_INTO_STORE }} ... ")
    configuration_id, debug, date_end, date_start, template = None, False, None, None, None

    if search is not None:
        search = unquote(search)
        query_params = parse_qs(search.lstrip("?"))

        configuration_id = query_params.get("configuration_id", [None])[0]
        debug = query_params.get("debug", [False])[0]
        date_end = query_params.get("date_end", [None])[0]
        date_start = query_params.get("date_start", [None])[0]
        template = query_params.get("template", [None])[0]

    if debug_btn_clicks:
        debug = not current_debug_state

    return configuration_id, debug, date_end, date_start, template

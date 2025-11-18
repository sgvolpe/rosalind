from dash import html


class SplashScreen:

    @staticmethod
    def as_html():
        return """
        <div class="last-page" > 
            <div class="last-row"> 
                <div class="last-col" style="width=1200px">
                    <p>
                    <img src="https://sabre-spark.s3.amazonaws.com/site_assets/images/design_foundations/logo_guidelines/sabre-logo-red.svg" 
                         alt="Sabre Logo" 
                         width="200" 
                         height="auto">
                         </p>
                </div>
            </div>
        </div>         
    """

    @staticmethod
    def as_dash():
        return html.Div(
            className="spark-splash-screen spark-main--sticky-footer",
            children=[
                html.Div(
                    className="spark-splash-screen__content",
                    children=[
                        html.Div(
                            className="spark-splash-screen__center",
                            children=[
                                html.I(className="spark-logo spark-logo--sabre spark-logo--lg"),
                                html.H1("KPI Reports", className="spark-splash-screen__heading")
                            ]
                        )
                    ]
                )
            ]
        )

from schemas.custom_report.cards import Cards

methods = [
    Cards.Stat.failure_rate

]
methods_dict = {
    k.uid: k.as_dash for k in methods
}

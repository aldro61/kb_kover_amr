"""
Generate reports for the app

"""

def generate_html_prediction_report(predictions):

    antibiotics = predictions[predictions.keys()[0]]["scm"].keys()

    report = \
"""
<html>
<head>
    <title>Kover Antimicrobial resistance prediction report</title>
</head>
<body>
{}
</body>
</html>
"""

    result_table = \
"""
<table>
    <tr>
        <th>Assembly</th>
        <th>Model</th>
        {}
    </tr>
</table>
""".format("\n".join(["<th>" + a + "</th>" for a in antibiotics]))

    return report.format(result_table)
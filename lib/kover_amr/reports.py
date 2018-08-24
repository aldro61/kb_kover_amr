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

    <!-- Bootstrap core CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
{}

<!-- Bootstrap core JavaScript
    ================================================== -->
<!-- Placed at the end of the document so the pages load faster -->
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>

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

<main role="main" class="container">

    <div class="starter-template">
    <h1>Bootstrap starter template</h1>
    <p class="lead">Use this document as a way to quickly start any new project.<br> All you get is this text and a mostly barebones HTML document.</p>
    </div>

</main>

""".format("\n".join(["<th>" + a + "</th>" for a in antibiotics]))

    return report.format(result_table)
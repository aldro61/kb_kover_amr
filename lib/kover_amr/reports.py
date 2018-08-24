"""
Generate reports for the app

"""
from urllib import quote


MODEL_BASE_URL = "https://github.com/aldro61/kb_kover_amr/tree/master/data/models/{}/{}/{}/README.md"


def generate_explanation_dialog(modal_id, assembly, antibiotic, species, algorithm, predicted_label, explanation):
    model_url = MODEL_BASE_URL.format(algorithm, quote(species.lower()), quote(antibiotic.lower().replace(" ", "_")))

    title = assembly.title() + " - " + antibiotic.title()

    explanation = "\n".join(explanation)

    modal_template = \
"""
<div class="modal fade" id="{0!s}" tabindex="-1" role="dialog" aria-labelledby="{0!s}Title" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="{0!s}Title">{1!s}</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        Prediction: {2!s}<br /><br />
        Reason:<br />
        {3!s}
      </div>
      <div class="modal-footer">
        <a href="{4!s}" target="_blank" class="btn btn-primary">View model</a>
      </div>
    </div>
  </div>
</div>
"""

    return modal_template.format(modal_id, title, predicted_label, explanation, model_url)


def generate_html_prediction_report(predictions, species):

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

    prediction_table_rows = []
    explanation_dialogs = []
    for assembly in predictions.keys():
        scm_row = \
"""
<tr>
    <td>{}</td>
    <td>SCM</td>
    {}
</tr>""".format(assembly, "\n".join(["<td class='{}'><button type='button' class='btn btn-link' data-toggle='modal' data-target='#{}'>{}</button>{}</td>".format("table-danger" if predictions[assembly]["scm"][a]["label"] == "resistant" else "table-success",
                                                                                                      str(hash(assembly + a + species)),
                                                                                                      predictions[assembly]["scm"][a]["label"],
                                                                                                      generate_explanation_dialog(str(hash(assembly + a + species)), assembly, a, species, "scm", predictions[assembly]["scm"][a]["label"], predictions[assembly]["scm"][a]["why"])) for a in antibiotics]))
        prediction_table_rows.append(scm_row)
        #explanation_dialogs += [generate_explanation_dialog(assembly, a, species, "scm", predictions[assembly]["scm"][a]["label"], predictions[assembly]["scm"][a]["why"]) for a in antibiotics]

        cart_row = \
"""
<tr>
    <td></td>
    <td>CART</td>
    {}
</tr>""".format("\n".join(["<td class='{}'><a href='{}' target='_blank'>{}</a></td>".format("table-danger" if predictions[assembly]["cart"][a]["label"] == "resistant" else "table-success",
                                                                                            MODEL_BASE_URL.format("cart", quote(species.lower()), quote(a.lower().replace(" ", "_"))),
                                                                                            predictions[assembly]["cart"][a]["label"]) for a in antibiotics]))
        prediction_table_rows.append(cart_row)

    result_table = \
"""
<table class="table table-striped table-bordered table-hover">
    <thead class="thead-dark">
        <tr>
            <th scope="col">Assembly</th>
            <th scope="col">Model</th>
            {}
        </tr>
    </thead>
    <tbody>
        {}
    </tbody>
</table>
""".format("\n".join(["<th scope='col'>" + a + "</th>" for a in antibiotics]),
           "\n".join(prediction_table_rows))

    #explanation_dialogs = "\n".join(explanation_dialogs)

    return report.format(result_table)
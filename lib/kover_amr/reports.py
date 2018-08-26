"""
Generate reports for the app

"""
from urllib import quote


MODEL_BASE_URL = "https://github.com/aldro61/kb_kover_amr/tree/master/data/models/{}/{}/{}/README.md"


def generate_explanation_id(assembly, antibiotic, species, algorithm):
    return "exp" + str(hash(algorithm + assembly + antibiotic + species)).replace("-", "a")

def generate_explanation_dialog(modal_id, assembly, antibiotic, species, algorithm, predicted_label, evidence):
    model_url = MODEL_BASE_URL.format(algorithm, quote(species.lower()), quote(antibiotic.lower().replace(" ", "_")))

    title = assembly.title()

    if algorithm == "cart":
        explanation = \
    """
    <div class="card">
    <div class="card-header">
        Evidence
    </div>
    <ul class="list-group list-group-flush">
        {}
    </ul>
    </div>
    """.format("\n".join(["<li class='list-group-item'>{}</li>".format(r) for r in evidence]) if len(evidence) > 0 else "<li class='list-group-item'>No predictive genomic markers of the phenotype were identified by the learning algorithm. The model always predicts this class, since it was the most abundant in the training data.</li>")

    elif algorithm == "scm":
        explanation = \
    """
    <div class="card">
    <div class="card-header">
        Evidence
    </div>
    <ul class="list-group list-group-flush">
        {}
    </ul>
    </div>
    """.format("\n".join(["<li class='list-group-item'>{}</li>".format(r) for r in evidence]) if len(evidence) > 0 and predicted_label == "resistant" else "<li class='list-group-item'>No evidence of resistance found.</li>")
    
    else:
        raise Exception("invalid algorithm")

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
        <p>
            <div class="card border-{6!s} mb-3" style="max-width: 18rem;">
                <div class="card-header">Predicted phenotype</div>
                <div class="card-body text-{6!s}">
                    <p class="card-text">{5!s} {2!s}</p>
                </div>
            </div>
        </p>
        <p>
            {3!s}
        </p>
      </div>
      <div class="modal-footer">
        <a href="{4!s}" target="_blank" class="btn btn-primary">View model</a>
      </div>
    </div>
  </div>
</div>
"""

    return modal_template.format(modal_id, title, predicted_label, explanation, model_url, antibiotic.title(), "success" if predicted_label == "susceptible" else "danger")


def generate_html_prediction_report(predictions, species):

    antibiotics = predictions[predictions.keys()[0]]["scm"].keys()

    report = \
"""
<html>
<head>
    <title>Kover Antimicrobial resistance prediction report</title>

    <!-- Bootstrap core CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet">

    <!-- Table text centering -->
    <style>
        table,
        thead,
        tr,
        tbody,
        th,
        td {{
            text-align: center;
        }}

        .table td {{
        text-align: center;   
        }}
    </style>

</head>
<body>

{}

<!-- Bootstrap core JavaScript
    ================================================== -->
<!-- Placed at the end of the document so the pages load faster -->
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>

<script type="text/javascript">
    $(document).ready(function() {{
        $('[data-toggle="tooltip"]').tooltip();
    }});
</script>

</body>
</html>
"""

    prediction_table_rows = []
    for assembly in predictions.keys():
        scm_row = \
"""
<tr>
    <td>{}</td>
    <td>SCM</td>
    {}
</tr>""".format(assembly, "\n".join(["<td class='{}'><span data-toggle='tooltip' title='Click for explanation'><button type='button' class='btn btn-link btn-sm' data-toggle='modal' data-target='#{}'>{}</button></span>{}</td>".format("table-danger" if predictions[assembly]["scm"][a]["label"] == "resistant" else "table-success",
                                                                                                      generate_explanation_id(assembly, a, species, "scm"),
                                                                                                      predictions[assembly]["scm"][a]["label"],
                                                                                                      generate_explanation_dialog(generate_explanation_id(assembly, a, species, "scm"), assembly, a, species, "scm", predictions[assembly]["scm"][a]["label"], predictions[assembly]["scm"][a]["why"])) for a in antibiotics]))
        prediction_table_rows.append(scm_row)

        cart_row = \
"""
<tr>
    <td></td>
    <td>CART</td>
    {}
</tr>""".format("\n".join(["<td class='{}'><span data-toggle='tooltip' title='Click for explanation'><button type='button' class='btn btn-link btn-sm' data-toggle='modal' data-target='#{}'>{}</button></span>{}</td>".format("table-danger" if predictions[assembly]["cart"][a]["label"] == "resistant" else "table-success",
                                                                                                      generate_explanation_id(assembly, a, species, "cart"),
                                                                                                      predictions[assembly]["cart"][a]["label"],
                                                                                                      generate_explanation_dialog(generate_explanation_id(assembly, a, species, "cart"), assembly, a, species, "cart", predictions[assembly]["cart"][a]["label"], predictions[assembly]["cart"][a]["why"])) for a in antibiotics]))
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

    return report.format(result_table)
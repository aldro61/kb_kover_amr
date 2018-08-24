"""
Generate reports for the app

"""
from urllib import quote


MODEL_BASE_URL = "https://github.com/aldro61/kb_kover_amr/tree/master/data/models/{}/{}/{}/README.md"


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

<!-- Modal -->
<div class="modal fade" id="exampleModalCenter" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLongTitle">Modal title</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        ...
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary">Save changes</button>
      </div>
    </div>
  </div>
</div>

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
    for assembly in predictions.keys():
        scm_row = \
"""
<tr>
    <td>{}</td>
    <td>SCM</td>
    {}
</tr>""".format(assembly, "\n".join(["<td class='{}'><button type='button' class='btn btn-link' data-toggle='modal' data-target='#exampleModalCenter'>{}</button></td>".format("table-danger" if predictions[assembly]["scm"][a]["label"] == "resistant" else "table-success",
                                                                                                      #MODEL_BASE_URL.format("scm", quote(species.lower()), quote(a.lower().replace(" ", "_"))),
                                                                                                      predictions[assembly]["scm"][a]["label"]) for a in antibiotics]))
        prediction_table_rows.append(scm_row)

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

    return report.format(result_table)
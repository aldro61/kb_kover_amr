/*
A KBase module: kover_amr
*/

module kover_amr {

    typedef string assembly_ref;

    /*
    Structure of input data for AMR prediction
    */
    typedef structure {
        assembly_ref assembly_input_ref;
        string species;
        string workspace_name;
    } AMRPredictionParams;

    /*
    Structure of output of AMR prediction
    */
    typedef structure {
        string report_name;
        string report_ref;
        int n_models_evaluated;
        int n_positive_preds;
        int n_negative_preds;
    } AMRPredictionResults;

    /*
    The AMR prediction function specification
    */
    funcdef predict_amr_phenotype(AMRPredictionParams params)
        returns (AMRPredictionResults output) authentication required;
};

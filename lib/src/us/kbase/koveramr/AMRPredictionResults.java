
package us.kbase.koveramr;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: AMRPredictionResults</p>
 * <pre>
 * Structure of output of AMR prediction
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report_name",
    "report_ref",
    "n_models_evaluated",
    "n_positive_preds",
    "n_negative_preds"
})
public class AMRPredictionResults {

    @JsonProperty("report_name")
    private String reportName;
    @JsonProperty("report_ref")
    private String reportRef;
    @JsonProperty("n_models_evaluated")
    private Long nModelsEvaluated;
    @JsonProperty("n_positive_preds")
    private Long nPositivePreds;
    @JsonProperty("n_negative_preds")
    private Long nNegativePreds;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("report_name")
    public String getReportName() {
        return reportName;
    }

    @JsonProperty("report_name")
    public void setReportName(String reportName) {
        this.reportName = reportName;
    }

    public AMRPredictionResults withReportName(String reportName) {
        this.reportName = reportName;
        return this;
    }

    @JsonProperty("report_ref")
    public String getReportRef() {
        return reportRef;
    }

    @JsonProperty("report_ref")
    public void setReportRef(String reportRef) {
        this.reportRef = reportRef;
    }

    public AMRPredictionResults withReportRef(String reportRef) {
        this.reportRef = reportRef;
        return this;
    }

    @JsonProperty("n_models_evaluated")
    public Long getNModelsEvaluated() {
        return nModelsEvaluated;
    }

    @JsonProperty("n_models_evaluated")
    public void setNModelsEvaluated(Long nModelsEvaluated) {
        this.nModelsEvaluated = nModelsEvaluated;
    }

    public AMRPredictionResults withNModelsEvaluated(Long nModelsEvaluated) {
        this.nModelsEvaluated = nModelsEvaluated;
        return this;
    }

    @JsonProperty("n_positive_preds")
    public Long getNPositivePreds() {
        return nPositivePreds;
    }

    @JsonProperty("n_positive_preds")
    public void setNPositivePreds(Long nPositivePreds) {
        this.nPositivePreds = nPositivePreds;
    }

    public AMRPredictionResults withNPositivePreds(Long nPositivePreds) {
        this.nPositivePreds = nPositivePreds;
        return this;
    }

    @JsonProperty("n_negative_preds")
    public Long getNNegativePreds() {
        return nNegativePreds;
    }

    @JsonProperty("n_negative_preds")
    public void setNNegativePreds(Long nNegativePreds) {
        this.nNegativePreds = nNegativePreds;
    }

    public AMRPredictionResults withNNegativePreds(Long nNegativePreds) {
        this.nNegativePreds = nNegativePreds;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((((("AMRPredictionResults"+" [reportName=")+ reportName)+", reportRef=")+ reportRef)+", nModelsEvaluated=")+ nModelsEvaluated)+", nPositivePreds=")+ nPositivePreds)+", nNegativePreds=")+ nNegativePreds)+", additionalProperties=")+ additionalProperties)+"]");
    }

}

"""
Set Covering Machine model

"""
import json
import os

from Bio.Seq import Seq


class SCMModel():
    def __init__(self, path):
        """
        Initialize the model based on description files

        """
        self.path = path
        model_info = json.load(open(os.path.join(path, "results.json"), "r"))["model"]
        self.rules = model_info["rules"]
        self.type = model_info["type"]
        del model_info

    def predict(self, kmers):
        """
        Predict phenotype based on k-mers (dict)

        Resistant = 1, Susceptible = 0

        """
        if not isinstance(kmers, set):
            raise Exception("Expected k-mers the be a dict.")

        rules_true = []
        rules_false = []
        for rule in self.rules:
            km = rule.replace("Presence(", "").replace("Absence(", "").replace(")", "")
            km_rc = str(Seq(km).reverse_complement())

            if "Presence" in rule and (km in kmers or km_rc in kmers):
                rules_true.append(rule)
            elif "Absence" in rule and not (km in kmers or km_rc in kmers):
                rules_true.append(rule)
            else:
                rules_false.append(rule)

        if self.type == "conjunction":
            predicted_pheno = 1 if len(rules_true) == len(self.rules) else 0
        else:
            predicted_pheno = 1 if len(rules_true) > 0 else 0
        
        # Pretty printing
        predicted_pheno = "resistant" if predicted_pheno == 1 else "susceptible"
        return predicted_pheno, rules_true

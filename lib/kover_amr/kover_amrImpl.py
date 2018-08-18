# -*- coding: utf-8 -*-
#BEGIN_HEADER
# XXX: Do not delete the BEGIN and END tags. These ensure that the code is preserved when running "make"
import json
import os

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from Bio import SeqIO
from Bio.Seq import Seq

MODEL_DIR = "/data/models"

# TODO: when looking for model k-mers also check for the reverse complement! (see SCMModel for example)
class CARTModel():
    def __init__(self, path):
        """
        Initialize the model based on description files

        """
        self.path = path

    def predict(self, kmers):
        """
        Predict phenotype based on k-mers (dict)

        Resistant = 1, Susceptible = 0

        """
        return 0


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
        if not isinstance(kmers, dict):
            raise Exception("Expected k-mers the be a dict.")

        hits = []
        for rule in self.rules:
            km = rule.replace("Presence(", "").replace("Absence(", "").replace(")", "")
            km_rc = str(Seq("ACCTGAGCGAGACCAGAGAGACCA").reverse_complement())

            if "Presence" in rule and (km in kmers or km_rc in kmers):
                hits.append(rule)
            elif "Absence" in rule and not (km in kmers or km_rc in kmers):
                hits.append(rule)

        if self.type == "conjunction":
            predicted_pheno = 1 if len(hits) == len(self.rules) else 0
        else:
            predicted_pheno = 1 if len(hits) > 0 else 0
        
        return predicted_pheno, hits

#END_HEADER


class kover_amr:
    '''
    Module Name:
    kover_amr

    Module Description:
    A KBase module: kover_amr
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    def get_assembly_info(self, ref):
        assembly_util = AssemblyUtil(self.callback_url)
        file = assembly_util.get_assembly_as_fasta({'ref': ref})
        return dict(name=file["assembly_name"], contigs=list(SeqIO.parse(file['path'], 'fasta')))

    def get_models_by_algorithm_and_species(self, algorithm, species):
        def prettyprint_antibiotic(name):
            name = name.title()
            name = name.replace("_", " ")
            return name

        model_root = os.path.join(MODEL_DIR, "{}/{}".format(algorithm, species))
        antibiotics = os.listdir(model_root)
        
        if algorithm == "scm":
            models = [SCMModel(os.path.join(model_root, a)) for a in antibiotics]
        elif algorithm == "cart":
            models = [CARTModel(os.path.join(model_root, a)) for a in antibiotics]
        else:
            raise Exception("Unsupported algorithm")

        return {prettyprint_antibiotic(a): m for a, m in zip(antibiotics, models)}


    def extract_kmers(self, fasta_path, k):
        """

        """
        assembly_id = str(hash(fasta_path))
        os.system("kmc -k{0:d} -fm -ci1 -cs1 {1!s} {2!s}/{3!s}.kmc.out .".format(k, fasta_path, self.scratch, assembly_id))
        os.system("kmc_dump {0!s}/{1!s}.kmc.out {0!s}/{1!s}.{2:d}.kmrs".format(self.scratch, assembly_id, k))
        os.system("rm {0!s}/{1!s}.kmc.out.kmc_pre".format(self.scratch, assembly_id))
        os.system("rm {0!s}/{1!s}.kmc.out.kmc_suf".format(self.scratch, assembly_id))
        kmers = [l.strip() for l in open("{0!s}/{1!s}.{2:d}.kmrs".format(self.scratch, assembly_id, k), "r")]
        os.system("rm {0!s}/{1!s}.{2:d}.kmrs".format(self.scratch, assembly_id, k))
        return kmers

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        #END_CONSTRUCTOR
        pass


    def predict_amr_phenotype(self, ctx, params):
        """
        The AMR prediction function specification
        :param params: instance of type "AMRPredictionParams" (Structure of
           input data for AMR prediction) -> structure: parameter
           "assembly_input_ref" of type "assembly_ref", parameter "species"
           of String, parameter "workspace_name" of String
        :returns: instance of type "AMRPredictionResults" (Structure of
           output of AMR prediction) -> structure: parameter "report_name" of
           String, parameter "report_ref" of String, parameter
           "n_models_evaluated" of Long, parameter "n_positive_preds" of
           Long, parameter "n_negative_preds" of Long
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN predict_amr_phenotype


        # Input validation
        for name in ['assembly_ref', 'species', 'workspace_name']:
            if name not in params:
                raise ValueError('Parameter "' + name + '" is required but missing')
        if not (isinstance(params['assembly_ref'], basestring) or isinstance(params['assembly_ref'], list)) or not len(params['assembly_ref']):
            raise ValueError('Pass in a valid assembly reference string(s)')

        # Extract params
        if not isinstance(params["assembly_ref"], list):
            assemblies = [params["assembly_ref"]]
        else:
            assemblies = params["assembly_ref"]
        species = params["species"]

        # Get models for species
        scm_models = self.get_models_by_algorithm_and_species("scm", species)

        # Process assemblies
        assembly_util = AssemblyUtil(self.callback_url)
        for assembly_ref in assemblies:

            # Get the fasta file path and other info
            assembly = assembly_util.get_assembly_as_fasta({'ref': assembly_ref})

            # Extract the k-mers
            kmers = self.extract_kmers(assembly["path"], k=31)
            kmers = dict(zip(kmers, [True] * len(kmers)))
            print "Kmers --", assembly["assembly_name"], ":", len(kmers)

            # Make predictions (SCM)
            for antibiotic, model in scm_models.iteritems():
                print antibiotic, model.predict(kmers)

            # Make predictions (CART)
            for antibiotic, model in cart_models.iteritems():
                print antibiotic, model.predict(kmers)

        output = {}

        #END predict_amr_phenotype

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method predict_amr_phenotype return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]

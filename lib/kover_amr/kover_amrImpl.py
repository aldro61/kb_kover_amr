# -*- coding: utf-8 -*-
#BEGIN_HEADER
# XXX: Do not delete the BEGIN and END tags. These ensure that the code is preserved when running "make"
import json
import os

from six import string_types
import numpy as np

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from Bio import SeqIO
from KBaseReport.KBaseReportClient import KBaseReport

from kover_amr.models.cart import CARTModel
from kover_amr.models.scm import SCMModel
from kover_amr.reports import generate_html_prediction_report


MODEL_DIR = "./data/models"
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
    GIT_URL = "git@github.com:aldro61/kb_kover_amr.git"
    GIT_COMMIT_HASH = "a0f997ebb89297e55884a12bf29e2f234cfdf50f"

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
        Get the k-mers that are in an assembly

        """
        assembly_id = str(hash(fasta_path))
        os.system("kmc -k{0:d} -fm -ci1 -cs1 {1!s} {2!s}/{3!s}.kmc.out .".format(k, fasta_path, self.scratch, assembly_id))
        os.system("kmc_dump {0!s}/{1!s}.kmc.out {0!s}/{1!s}.{2:d}.kmrs".format(self.scratch, assembly_id, k))
        os.system("rm {0!s}/{1!s}.kmc.out.kmc_pre".format(self.scratch, assembly_id))
        os.system("rm {0!s}/{1!s}.kmc.out.kmc_suf".format(self.scratch, assembly_id))
        kmers = set([l.strip().split('\t')[0] for l in open("{0!s}/{1!s}.{2:d}.kmrs".format(self.scratch, assembly_id, k), "r")])
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
           String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN predict_amr_phenotype

        # Input validation
        for name in ['assembly_input_ref', 'species', 'workspace_name']:
            if name not in params:
                raise ValueError('Parameter "' + name + '" is required but missing')
        if not (isinstance(params['assembly_input_ref'], string_types) or isinstance(params['assembly_input_ref'], list)) or not len(params['assembly_input_ref']):
            raise ValueError('Pass in a valid assembly reference string(s)')

        # Extract params
        if not isinstance(params["assembly_input_ref"], list):
            assemblies = [params["assembly_input_ref"]]
        else:
            assemblies = params["assembly_input_ref"]
        species = params["species"]

        # Get models for species
        scm_models = self.get_models_by_algorithm_and_species("scm", species)
        cart_models = self.get_models_by_algorithm_and_species("cart", species)

        # Process assemblies
        predictions = {}
        assembly_util = AssemblyUtil(self.callback_url)
        
        for assembly_ref in assemblies:
            
            assembly_predictions = {}

            # Get the fasta file path and other info
            assembly = assembly_util.get_assembly_as_fasta({'ref': assembly_ref})

            # Extract the k-mers
            kmers = self.extract_kmers(assembly["path"], k=31)
            print "Kmers --", assembly["assembly_name"], ":", len(kmers)

            # Make predictions (SCM)
            print "SCM models"
            assembly_predictions["scm"] = {}
            for antibiotic, model in scm_models.iteritems():
                p = model.predict(kmers)
                assembly_predictions["scm"][antibiotic]["label"] = p[0]
                assembly_predictions["scm"][antibiotic]["why"] = p[1]

            # Make predictions (CART)
            print "CART models"
            assembly_predictions["cart"] = {}
            for antibiotic, model in cart_models.iteritems():
                p = model.predict(kmers)
                assembly_predictions["cart"][antibiotic]["label"] = p[0]
                assembly_predictions["cart"][antibiotic]["why"] = p[1]

            predictions[assembly["assembly_name"]] = assembly_predictions
            del assembly_predictions

        # Generate report
        text_message = "This is a test report for kover amr (text)"

        # Data for creating the report, referencing the assembly we uploaded
        report_data = {
            'objects_created': [],
            'text_message': text_message,
            'direct_html': generate_html_prediction_report(predictions)
        }

        # Initialize the report
        kbase_report = KBaseReport(self.callback_url)
        report = kbase_report.create({
            'report': report_data,
            'workspace_name': params['workspace_name']
        })

        output = {
            'report_ref': report['ref'],
            'report_name': report['name']
        }

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

# -*- coding: utf-8 -*-
#BEGIN_HEADER
# XXX: Do not delete the BEGIN and END tags. These ensure that the code is preserved when running "make"
import json
import os

from six import string_types
import numpy as np
import re

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from Bio import SeqIO
from Bio.Seq import Seq
from KBaseReport.KBaseReportClient import KBaseReport

MODEL_DIR = "/data/models"

class CARTModel():
    def __init__(self, path):
        """
        Initialize the model based on description files

        """
        self.path = path
        try:
            self.tree = TreeParser(os.path.join(self.path, "model.fasta")).get_tree()
        except:
            self.tree = get_majority_class_tree(self.path)

    def predict(self, kmers):
        """
        Predict phenotype based on k-mers (dict)

        Resistant = 1, Susceptible = 0

        """
        if not isinstance(kmers, set):
            raise Exception("Expected k-mers the be a dict.")

        decision_path = []
        def _apply_model(node):
            if node.is_leaf:
                return 1 if node.resistant > node.sensitive else 0
                
            else:
                km = node.kmer
                km_rc = str(Seq(km).reverse_complement())
                if (km in kmers or km_rc in kmers):
                    decision_path.append("Presence({})".format(km))
                    return _apply_model(node.left)
                else:
                    decision_path.append("Absence({})".format(km))
                    return _apply_model(node.right)
            
        predicted_pheno = _apply_model(self.tree)
        return predicted_pheno, decision_path


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

        hits = []
        for rule in self.rules:
            km = rule.replace("Presence(", "").replace("Absence(", "").replace(")", "")
            km_rc = str(Seq(km).reverse_complement())

            if "Presence" in rule and (km in kmers or km_rc in kmers):
                hits.append(rule)
            elif "Absence" in rule and not (km in kmers or km_rc in kmers):
                hits.append(rule)

        if self.type == "conjunction":
            predicted_pheno = 1 if len(hits) == len(self.rules) else 0
        else:
            predicted_pheno = 1 if len(hits) > 0 else 0
        
        return predicted_pheno, hits
        
class TreeNode(object):
    def __init__(self, kmer=None):
        self.kmer = kmer
        self.parent = None
        
    @property
    def is_leaf(self):
        return self.kmer is None
        
class TreeParser(object):
    
    def __init__(self, input_path):
        self.input_path = input_path
        self.tree = None
        self.parse()
        
    def get_tree(self):
        if self.tree is None:
            raise RuntimeError("Tree is None")
        else:
            return self.tree
        
    def extract_rule_id(self, header):
        return int(header.split(",")[0].split(":")[-1].split("___")[0])
        
    def extract_rule_node(self, header, kmer):
        spt = header.split(",")
        ex = spt[0].split(":")[-1].split("___")[1].split("_")[1]
        eq = spt[0].split(":")[-1].split("___")[2].split("_")[1]
        imp = float(spt[-1].split(":")[-1].lstrip())
        node = TreeNode(kmer=kmer)
        node.nb_examples = ex
        node.eq_rules = eq
        node.importance = imp
        return node
        
    def extract_class_probas(self, header):
        spt = header.split("___")[2].split("__")
        classes, probas = zip(*[(class_info.split("_")[0], float(class_info.split("_")[2])) for class_info in spt])
        return {c:p for c,p in zip(classes, probas)}
        
    def extract_children(self, header):
        spt = header.split(",")
        left = spt[1].split(":")[-1].strip()
        right = spt[2].split(":")[-1].strip()

        try:
            left = int(left.split("___")[0])
            left = self.rule_dict[left]
        except:
            class_probas = self.extract_class_probas(left)
            ex = left.split("___")[1].split("_")[1]
            left = TreeNode()
            left.nb_examples = ex
            left.resistant = class_probas["resistant"]
            left.sensitive = class_probas["sensitive"]
        
        try:
            right = int(right.split("___")[0])
            right = self.rule_dict[right]
        except:
            class_probas = self.extract_class_probas(right)
            ex = right.split("___")[1].split("_")[1]
            right = TreeNode()
            right.nb_examples = ex
            right.resistant = class_probas["resistant"]
            right.sensitive = class_probas["sensitive"]
            
        return left, right
        
    def find_root(self):
        roots = [id for id in self.rule_dict if self.rule_dict[id].parent is None]
        assert len(roots) == 1
        return roots[0]
            
    def parse(self):
        self.rules = list(zip(*fasta_to_contigs(self.input_path, return_headers=True)[::-1]))
        
        self.rule_dict = {self.extract_rule_id(header): self.extract_rule_node(header, kmer) for header, kmer in self.rules}
        
        for header, kmer in self.rules:
            current_rule = self.rule_dict[self.extract_rule_id(header)]
            
            left, right = self.extract_children(header)
            
            current_rule.left = left
            current_rule.right = right
            
            left.parent = current_rule
            right.parent = current_rule
        
        self.tree = self.rule_dict[self.find_root()]


def fasta_to_contigs(path, return_headers=False):
    """
    Reads a FASTA file and loads its contigs
    Note: sequences are returned in upper case
    """
    contigs = []
    headers = []
    def add_contig(header, seq):
        if len(seq) == 0:
            raise Exception("Attempted to add a contig with length 0. Not normal! Path is " + path)
        contigs.append(seq.upper())
        headers.append(header.lower())

    buffer = ""
    header = ""
    for l in open(path, "r"):
        if l.startswith(">"):
            # New contig starting

            # Save current sequence and flush buffer
            if len(buffer) > 0.:
                add_contig(header, buffer)
                buffer = ""

            # Read contig header
            header = l[1:].strip()

        else:
            # Accumulate DNA sequence
            buffer += l.strip()

    # Save final buffer
    if buffer is not None and buffer != "":
        add_contig(header, buffer)

    if return_headers:
        return contigs, headers
    else:
        return contigs


def get_majority_class_tree(path):
    with open(os.path.join(path, "report.txt"), 'r') as report_file:
        report = report_file.read()
    m = re.search("training\: ([0-9]*) \(Group sensitive: ([0-9]*), Group resistant: ([0-9]*)\)", report)
    tree = TreeNode()
    tree.nb_examples = int(m.group(1))
    tree.sensitive = int(m.group(2))
    tree.resistant = int(m.group(3))
    return tree

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
        if not (isinstance(params['assembly_ref'], string_types) or isinstance(params['assembly_ref'], list)) or not len(params['assembly_ref']):
            raise ValueError('Pass in a valid assembly reference string(s)')

        # Extract params
        if not isinstance(params["assembly_ref"], list):
            assemblies = [params["assembly_ref"]]
        else:
            assemblies = params["assembly_ref"]
        species = params["species"]

        # Get models for species
        scm_models = self.get_models_by_algorithm_and_species("scm", species)
        cart_models = self.get_models_by_algorithm_and_species("cart", species)

        # Process assemblies
        assembly_util = AssemblyUtil(self.callback_url)
        for assembly_ref in assemblies:

            # Get the fasta file path and other info
            assembly = assembly_util.get_assembly_as_fasta({'ref': assembly_ref})

            # Extract the k-mers
            kmers = self.extract_kmers(assembly["path"], k=31)
            print "Kmers --", assembly["assembly_name"], ":", len(kmers)

            # Make predictions (SCM)
            print "SCM models"
            for antibiotic, model in scm_models.iteritems():
                print antibiotic, model.predict(kmers)

            # Make predictions (CART)
            print "CART models"
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

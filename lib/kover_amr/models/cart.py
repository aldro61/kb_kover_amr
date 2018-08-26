"""
Classification Tree model

"""
import os
import re

from Bio.Seq import Seq


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
        
        # Pretty printing
        predicted_pheno = "resistant" if _apply_model(self.tree) == 1 else "susceptible"
        return predicted_pheno, {"decision_path": decision_path}

        
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
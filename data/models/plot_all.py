import argparse

import os
from os.path import join, isfile, isdir
from os import listdir, stat

from plot_model import visualize_model

def run_directory(root_dir, filename):
	dirs = [d for d in listdir(root_dir) if isdir(join(root_dir, d))]
	files = [f for f in listdir(root_dir) if isfile(join(root_dir, f))]

	if filename in files:
		if stat(join(root_dir, filename)).st_size != 0 and "fasta" in filename:
			print("\nProcessing {}".format(root_dir))
			visualize_model(join(root_dir, filename))

			os.system("convert -density 150 '{}' '{}'".format(join(root_dir, "model.pdf"), join(root_dir, "model.png")))

	for d in dirs:
		run_directory(join(root_dir, d), filename)

def main():
	# Parser
	parser = argparse.ArgumentParser(description="Run model interpretability on a folder")
	parser.add_argument('--dir', type=str, default=".")
	parser.add_argument('--filename', type=str, default="model.fasta")

	args = parser.parse_args()
	run_directory(args.dir, args.filename)

	print("### DONE ###")

if __name__ == '__main__':
	main()

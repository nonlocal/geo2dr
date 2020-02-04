"""
Experimental scrip which runs, sets up and builds distributed representations of graphs
using the graphlets as the main form of subgraph pattern to create datasets
for distributive modelling

Hyperparameters are decomposition algorithm and skipgram specific. Graphlets have the
following hyperparameters
- num_graphlets
- samplesize

skipgram has the following hyperparameters
- embedding_dimensions
- batch_sizes
- epochs
- initial_learning rate(fixed for now)
- min_count (on number of subgraph patterns)

It will also do this <run> number of times for empirical testing of standard deviation

Author: Paul Scherer
"""

import embedding_methods.utils as utils
from decomposition.graphlet_patterns import graphlet_corpus
from embedding_methods.classify import cross_val_accuracy
from embedding_methods.trainer import Trainer

# graphlet hyperparameters
num_graphlets = range(2,9)
samplesizes = range(1,10,2)

# skipgram hyperparameters
min_counts = [1, 2]
embedding_dimensions = [8, 16, 32, 64, 128]
batch_size = 128
runs = 5
epochs = 500
initial_lr = 0.001

embedding_folder = "embeddings"
dataset = "MUTAG"
corpus_dir = "/home/morio/workspace/geo2dr/geometric2dr/file_handling/dortmund_gexf/" + dataset

for num_graphlet in num_graphlets:
	for samplesize in samplesizes:
		extension = ".graphlet_ng_"+str(num_graphlet)+"_ss_"+str(samplesize)
		for embedding_dimension in embedding_dimensions:
			for min_count in min_counts:
				for run in range(runs):
					output_fh = str.join("_", [dataset, "GLET", "NG", str(num_graphlet), "SS", str(samplesize), "embd", str(embedding_dimension), "epochs", str(epochs), "bs", str(batch_size), "minCount", str(min_count), "run", str(run)])
					output_fh += ".json"
					output_fh = embedding_folder + "/" + output_fh

					# Run the decomposition algorithm
					graph_files = utils.get_files(corpus_dir, ".gexf", max_files=0)
					print("###.... Loaded %s files in total" % (str(len(graph_files))))
					print(output_fh)
					graphlet_corpus(corpus_dir, num_graphlet, samplesize)

					# Use the graph documents in the directory to create a trainer which handles creation of datasets/corpus/dataloaders
					# and the skipgram model.
					trainer = Trainer(corpus_dir=corpus_dir, extension=extension, max_files=0, output_fh=output_fh,
					                  emb_dimension=embedding_dimension, batch_size=batch_size, epochs=epochs, initial_lr=initial_lr,
					                  min_count=min_count)
					trainer.train()

					# Classification if needed
					final_embeddings = trainer.skipgram.give_target_embeddings()
					graph_files = trainer.corpus.graph_fname_list
					class_labels_fname = "/home/morio/workspace/geo2dr/geometric2dr/file_handling/MUTAG.Labels"
					embedding_fname = trainer.output_fh
					classify_scores = cross_val_accuracy(corpus_dir, trainer.corpus.extension, embedding_fname, class_labels_fname)
					mean_acc, std_dev = classify_scores
					print("Mean accuracy using 10 cross fold accuracy: %s with std %s" % (
					    mean_acc, std_dev))
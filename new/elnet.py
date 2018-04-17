#!/usr/bin/env python

# Elastic Net Classification

import sys
import pandas as pd
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.cross_validation import cross_val_score, StratifiedKFold
from weighted_ks import calcKS
from hyperopt import hp, fmin, tpe, rand
from math import log

from argparse import ArgumentParser
from parseFields import parseFields
from time import time, strftime
import json
import pickle as pkl
from os.path import abspath

parser = ArgumentParser(description='A tool for running elastic net classification')

parser.add_argument('train')
parser.add_argument('test')
parser.add_argument('-x','--x_vars',default=None,type=str,help='Independent (X) variable columns[Linux-style parsing]')
parser.add_argument('-y','--y_var',default=None,type=int,help='Dependent (Y) variable column')
parser.add_argument('-w','--weights',default=None,type=int,help='Weights column (if present)')
parser.add_argument('-k','--k_folds',default=1,type=int,help='Number (k) of folds for cross_validation [default: 1]')
parser.add_argument('-e','--evals',default=None,type=int,help='Number of evaluations for hyperparameter search [default: None]')
parser.add_argument('-d','--delimiter',default='|',type=str,help='Input file delimiter [default: "|"]')
parser.add_argument('-s','--seed',default=2813308004,type=int,help='Random seed [default: 2813308004]')
parser.add_argument('-o','--output',default=None,type=str,help='Save final model to pkl [default: None]')
#parser.add_argument('-m','--metric',help='metric to minimize')
parser.add_argument('-c','--config',default=None,help='Configuration file (overrides command line options) [default: None]')

args = parser.parse_args()

#METRIC = 'metric'
METRIC = 'KS'
metric_func = calcKS

def load_data(data_file, x_vars, y_var, weights):
	if x_vars is None or y_var is None:
		print "Must provide X and Y vars"
		sys.exit(1)
	else:
		x_vars = parseFields(x_vars)
		y_var = y_var - 1
		data = pd.read_csv(open(data_file), delimiter=args.delimiter)
		index = 0
		if weights is not None:
			index += 1
			weights = weights - 1
			data = data[[weights] + [y_var] + x_vars]
		else:
			data = data[[y_var] + x_vars]
		header = list(data.columns)[1+index:]
		target = list(data.columns)[index]
		XY = data.as_matrix()
		Y = XY[:,index]
		X = XY[:,index+1:]
		W = XY[:,0] if weights else np.ones(XY.shape[0])
		return X,Y,W,target,header

def train_fold(estimator, X, Y, W, train_index, test_index, metric):
	estimator.fit(X[train_index,:], Y[train_index])
	y_pred = estimator.predict_proba(X[test_index,:])
	return metric(Y[test_index], y_pred[:,1], W[test_index])

def cv_score(estimator, X, Y, W, k, metric):
	cv = StratifiedKFold(Y, n_folds = k, shuffle = True, random_state = args.seed)
	scores = [train_fold(estimator, X, Y, W, train_index, test_index, metric) for train_index, test_index in cv]
	return np.array(scores)

# Function to fit one iteration given a set of hyperparameters
# called in run_wrapper
def run_test(parameters):
	alpha, l1_ratio, eta = parameters

	alpha = float(alpha)
	l1_ratio = float(l1_ratio)
	eta = float(eta)

	print "Alpha:", alpha
	print "L1 ratio:", l1_ratio
	print "Learning_rate (eta):", eta

	elnet = SGDClassifier(loss='log',penalty='elasticnet',alpha=alpha,l1_ratio=l1_ratio, eta0=eta,
			fit_intercept=True,max_iter=250,shuffle=True,random_state=args.seed,verbose=0,n_jobs=1,
			learning_rate='constant',warm_start=True)
	if args.k_folds > 1:
		scores = cv_score(elnet, X_train, Y_train, W_train, k=args.k_folds, metric=metric_func)
	else:
		train_index = test_index = range(X_train.shape[0])
		scores = train_fold(elnet, X_train, Y_train, W_train, train_index, test_index, metric_func)

	return scores

def run_wrapper(parameters):
	global RUN_COUNTER
	global BEST_SCORE

	RUN_COUNTER += 1
	print 'run', RUN_COUNTER

	start = time()
	scores = run_test(parameters)
	score = np.mean(scores)
	# update best score
	if score < BEST_SCORE:
		BEST_SCORE = score

	print
	print "%s: %.3f" % (METRIC, score)
	print "Scores: ", scores
	print "Elapsed: ", int(round(time()- start))
	print
	print "Best score: %.3f" % BEST_SCORE

	return score

### BUILD MODEL ###

# Collect metadata if output is specified
if args.output:
	model_type = raw_input("Input model type.\n")
	model_type = model_type.strip()
	model_desc = raw_input("Provide breif model description.\n")
	model_desc = model_desc.strip()

print "Loading data."
X_train,Y_train,W_train,target_train,header_train = load_data(args.train,args.x_vars,args.y_var,args.weights)
X_test,Y_test,W_test,target_test,header_test = load_data(args.test,args.x_vars,args.y_var,args.weights)
assert(target_train == target_test)
assert(header_train == header_test)
print "Training data contains %i rows and %i features." % X_train.shape
print "Test data contains %i rows and %i features." % X_test.shape
print "Metric to optimize: %s" % METRIC

# run hyperopt if max_evals provided
# this saves parameters in dictionary called BEST
if args.evals:
	# hyperparameter search space
	space = (hp.loguniform('alpha',log(0.00001),log(1)),
			hp.uniform('l1_ratio',0.01,1),
			hp.loguniform('eta', log(1e-3), log(1)),
			)

	RUN_COUNTER = 0
	BEST_SCORE = np.inf
	start_time = time()
	BEST = fmin(run_wrapper, space, algo = rand.suggest, max_evals = args.evals)

	# End hyperopt
	print "Seconds passed:", int(round(time() - start_time))
	print BEST
	print "Score for best hyperparameters: %f.3" % BEST_SCORE

# BEST dictionary contains parameters from hyperopt or config, whichever is provided
# train final model if output provided
if args.output:
	# train with best hyperparameters
	alpha = float(BEST['alpha'])
	l1_ratio = float(BEST['l1_ratio'])
	eta = float(BEST['eta'])
	print "Training model with best set of hyperparameters."
	print "Alpha:", alpha
	print "L1 ratio:", l1_ratio
	print "Learning_rate (eta):", eta

	# train model with BEST hyperparameters
	elnet = SGDClassifier(loss='log',penalty='elasticnet',alpha=alpha,l1_ratio=l1_ratio, eta0=eta,
			fit_intercept=True,max_iter=250,shuffle=True,random_state=args.seed,verbose=0,n_jobs=1,
			learning_rate='constant',warm_start=True)
	elnet.fit(X_train, Y_train)

	# calculate cross-validation metrics if config option provided
	if args.config:
		if cross_validate:
			print "Calculating cross-validated %s" % METRIC
			scores = cv_score(elnet, X_train, Y_train, W_train, k, metric_func)
			BEST_SCORE = np.mean(scores)
		else:
			BEST_SCORE = None

	# Calculate metric
	preds_train = elnet.predict_proba(X_train)[:,1]
	metric_train = metric_func(Y_train,preds_train,W_train)
	preds_test = elnet.predict_proba(X_test)[:,1]
	metric_test = metric_func(Y_test,preds_test,W_test)

	# save model to pkl object
	if args.output.split('.')[-1] != "pkl":
		args.output = args.output + ".pkl"
	print "Saving model to %s" %args.output
	output = {}
	output['model'] = elnet
	output['metric'] = METRIC
	output['cv_score'] = np.abs(BEST_SCORE) if BEST_SCORE else None
	output['train_score'] = metric_train
	output['test_score'] = metric_test
	output['parameters'] = BEST
	output['creation_date'] = strftime("%c")
	output['training_data'] = abspath(args.train)
	output['test_data'] = abspath(args.test)
	output['variables'] = header_train
	output['model_type'] = model_type
	output['model_description'] = model_desc
	output['target'] = target_train
	output['configuration'] = {}
	if args.config:
		output['configuration']['run_type'] = 'config file'
		output['configuration']['options'] = config
	else:
		output['configuration']['run_type'] = 'hyperopt'
		output['configuration']['options'] = {}
		output['configuration']['options']['options'] = vars(args)
	with open(args.output,'w') as m:
		pkl.dump(output,m)

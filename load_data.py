#!/usr/bin/env python

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

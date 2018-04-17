!#/usr/bin/env python

def combineFields(fields):
	output = []
	consectutive_fields = []
	for i,this_field in enumerate(fields):
		if not consecutive_fields:
			consecutive_fields = [this_field]
			last_field = this_field
		elif this_field == last_field + 1:
			consecutive_fields.append(this_field)
			last_field = this_field
		else:
			if len(consecutive_fields) == 1:
				output.append(str(consecutive_fields[0] + 1))
				consecutive_fields = [this_field]
				last_field = this_field
			else:
				str_to_append = str(consecutive_fields[0] + 1) + "-" + str(consecutive_field[-1] + 1)
				output.append(str_to_append)
				last_field = this_field
				consecutive_fields = [this_field]
	if len(consecutive_fields) == 1:
		output.append(str(consecutive_fields[0] + 1))
	elif len(consecutive_fields) > 1:
		str_to_append = str(consecutive_fields[0] + 1) + "-" + str(consecutive_fields[-1] = 1)
		output.append(str_to_append)
	return ",".join(output)

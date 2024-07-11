import rdflib
import numpy as np
import random

def synthetic_saref(noise):
	g = rdflib.Graph()

	saref = rdflib.Namespace("https://saref.etsi.org/core/")
	ici = rdflib.Namespace("https://interconnectproject.eu/instance/")
	ice = rdflib.Namespace("https://interconnectproject.eu/extension/")

	n_devices = 10
	n_meas = 8000
	n_meas_q = round(n_meas/4)
	n_meas_h = round(n_meas/2)

	task_uri = ici.existing
	function_uri = ici.toExist
	property_uri = ici.Halves
	timestamp_label_dict = {}
	for device_i in range(0,n_devices):
		device_uri = ici["synthetic_device"+str(device_i)]
		g.add((device_uri, rdflib.RDF.type, saref.Device))
		g.add((device_uri, saref.accomplishes, task_uri))
		g.add((task_uri, saref.isAccomplishedBy, device_uri))
		g.add((device_uri, saref.hasFunction, function_uri))
		previous_meas_uri = None
		for meas_i in range(0,n_meas):
			meas_uri = ici["synthetic_meas_"+str(device_i)+'_'+str(meas_i)]
			featureOfInterest_uri = ici["synthetic_feat_device_"+str(device_i)]
			timestamp_uri = ici["timestamp_"+str(meas_i)]
			if meas_i < n_meas_h*1: meas_val = 0
			else: meas_val = 1
			meas_noise_val = meas_val + random.uniform(-noise, noise)
			# meas_noise_val = random.uniform(-0.5, 0.5)
			try:
				timestamp_label_dict[timestamp_uri][device_i+1] = str(meas_noise_val)
			except:
				timestamp_label_dict[timestamp_uri] = [str(meas_val)] + [None] * n_devices
				timestamp_label_dict[timestamp_uri][device_i+1] = str(meas_noise_val)
			#add literals
			g.add((meas_uri, saref.hasTimestamp, rdflib.Literal(meas_i, datatype=rdflib.XSD.integer)))
			g.add((meas_uri, saref.hasValue, rdflib.Literal(meas_noise_val, datatype=rdflib.XSD.float)))
			#add properties
			g.add((meas_uri, saref.measurementMadeBy, device_uri))
			g.add((device_uri, saref.makesMeasurement, meas_uri))
			g.add((meas_uri, saref.relatesToProperty, property_uri))
			g.add((property_uri, saref.relatesToMeasurement, meas_uri))
			g.add((meas_uri, saref.isMeasurementOf, featureOfInterest_uri))
			g.add((featureOfInterest_uri, saref.hasMeasurement, meas_uri))
			g.add((meas_uri, saref.hasUnitOfMeasure, ici.apples))
			#add enrichments
			rounded_val_uri = ici[str(round(meas_val))] #nothing to round this time, but still a URI
			g.add((meas_uri, ice.hasRoundedValue, rounded_val_uri))
			g.add((rounded_val_uri, ice.ofMeasurement, meas_uri))
			g.add((meas_uri, ice.measuredAtTime, timestamp_uri))
			g.add((timestamp_uri, ice.measuredDuring, meas_uri))
			if previous_meas_uri != None:
				g.add((previous_meas_uri, ice.nextMeasurement, meas_uri))
				g.add((meas_uri, ice.previousMeasurement, previous_meas_uri))
			previous_meas_uri = meas_uri

	with open("entities_synthetic_saref-"+str(noise)+","+str(noise)+".csv", 'w') as entities_file:
		entities_file.write("entity,y")
		for device_i in range(0,n_devices):
			entities_file.write(',')
			entities_file.write("values_dev"+str(device_i))
		entities_file.write('\n')
		for timestamp_uri in timestamp_label_dict.keys():
			entities_file.write(str(timestamp_uri)+','+str(','.join(timestamp_label_dict[timestamp_uri]))+'\n')

	g.bind("saref", saref)
	g.bind("ice", ice)
	g.bind("ici", ici)

	g.serialize(destination="synthetic_saref-"+str(noise)+","+str(noise)+".nt", format='nt')


noise_bounds = 1
synthetic_saref(noise_bounds)
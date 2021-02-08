#!/usr/bin/python3.6
import boto3
import csv

profile=''

with open("{}.csv".format(profile), 'w', newline='') as csvfile:
	header = ['Cluster', 'Total CPU units','Total memory','Free CPU units', 'Free memory', 'Free CPU %', 'Free memory %']
	writer = csv.DictWriter(csvfile, fieldnames = header)
	writer.writeheader()

	session = boto3.Session(profile_name=profile)
	ecsClient = session.client('ecs')

	clusterPaginator = ecsClient.get_paginator('list_clusters')
	clusterPages = clusterPaginator.paginate(
		PaginationConfig={
                        'MaxItems': 1000,
                        'PageSize': 50
                }
        )
	
	counter = 1;
	for page in clusterPages:
	#allClusters = ecsClient.list_clusters()
		for currentCluster in page['clusterArns']:
			print ("Processing cluster #"+str(counter))
			clusterCPU = 0
			clusterRAM = 0
			allCPU = 0
			allRAM = 0
			allInstances = ecsClient.list_container_instances(
				cluster = currentCluster	
			)
			for instance in allInstances['containerInstanceArns']:
				info = ecsClient.describe_container_instances(
					cluster = currentCluster,
					containerInstances=[instance]
				)
				resources = info['containerInstances'][0]['remainingResources']
				for availableResource in resources:
					if availableResource['name']=='CPU':
						clusterCPU+=availableResource['integerValue']
					if availableResource['name']=='MEMORY':
						clusterRAM+=availableResource['integerValue']

				allResources = info['containerInstances'][0]['registeredResources']
				for allocatedResource in allResources:
					if allocatedResource['name']=='CPU':
						allCPU+=allocatedResource['integerValue']
					if allocatedResource['name']=='MEMORY':
						allRAM+=allocatedResource['integerValue']
			if allCPU == 0:
				percentCPU=0
			else:
				percentCPU = format(clusterCPU/allCPU*100, '.2f')
			if allRAM == 0:
				percentRAM=0
			else:
				percentRAM = format(clusterRAM/allRAM*100, '.2f')
			row = {
				'Cluster': currentCluster.split('/')[1],
				'Total CPU units': str(allCPU),
				'Total memory':str(allRAM),
				'Free CPU units': str(clusterCPU),
				'Free memory': str(clusterRAM),
				'Free CPU %': str(percentCPU),
				'Free memory %': str(percentRAM)
			}
			writer.writerow(row)
			counter+=1

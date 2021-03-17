import sys
import git
import os
import yaml
import mysql.connector

def DBConnection(sql, values):
	try:
		print("Execute query -> "+sql)
		db = mysql.connector.connect(host="10.95.235.233", user="thor", password="thor_deployments", database="test")
		cr = db.cursor()
		cr.execute(sql, values)
		db.commit()
	except mysql.connector.Error as error:
		print("Failed to connet in the table {}".format(error))
	finally:
		cr.close()
		db.close()

def processDB(change, pathFile, fileChanged):
	print("Type change: "+change)
	idJira = fileChanged.split("/")[1].split(".yml")[0]
	print ("idJira" + idJira)
	if change == "A":
		print("Add new validation")
		with open(pathFile, 'r') as file:
			field_list = yaml.safe_load(file)
			print(field_list)
			for f in field_list:
				entity = f['dataset_id']
				id_validation = f['id']
				version = f['dataset_version']
				field = f['field']
				query = f['sql']
				description = f['description']
				metrics_value = '|'.join(s for s in f['metrics'])
				sources = '|'.join(s for s in f['sources'])
				values = (entity, version, id_validation, field, description, metrics_value, sources, query, idJira)
		print("Insert new validation into table")
		sql = "INSERT INTO test_thor4p (entity,version,id,field,description,metrics_value,sources,query,idJira) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		DBConnection(sql, values)
	elif change == "D":
		print("Delete a validation into table")
		sql = "DELETE FROM test_thor4p WHERE idJira = '%s'" %(idJira)
		DBConnection(sql,"")
	elif change == "M":
		print("Modificate a validation")
		with open(pathFile, 'r') as file:
			field_list = yaml.safe_load(file)
			print(field_list)
			for f in field_list:
				entity = f['dataset_id']
				id_validation = f['id']
				version = f['dataset_version']
				field = f['field']
				query = f['sql']
				description = f['description']
				metrics_value = '|'.join(s for s in f['metrics'])
				sources = '|'.join(s for s in f['sources'])
				values = (entity, version, field, description, metrics_value, sources, query, id_validation)
		sql = "UPDATE test_thor4p SET entity= %s, version= %s, field= %s, description= %s, metrics_value= %s, sources= %s, query=%s WHERE id=%s"
		DBConnection(sql, values)
	else:
		print("No data found for current parametrization")


def getChange(path):
	print("***PATH: "+ path)
	repo = git.Repo(path)
	#list branches
	print("list branches")
	for h in repo.heads:
		print ("branch-> " + h)
	#commit = repo.git.diff('HEAD~1..HEAD', name_status=True)
	commit = repo.git.diff('HEAD~1..main', name_status=True)
	type = commit.split("\t")[0]
	fileChanged = commit.split("\t")[1]
	pathFile = path + "/" + fileChanged
	print ("type" + type)
	print ("pathFile" + pathFile)
	return type, pathFile, fileChanged


def main(args):
	print("Inicializacion")
	path = sys.argv[1]
	type, pathFile, fileChanged = getChange(path)
	processDB(type, pathFile, fileChanged)

if __name__ == "__main__":
	main(sys.argv[1:])

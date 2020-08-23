import json

with open("classification_words.json", "r") as categories_file:
	categories_dict = json.load(categories_file)
	with open("profesiones.txt", "r") as profesiones_file:
		for line in profesiones_file:
			profesiones = line.split(" ")
			last = profesiones[-1]
			if last != '':
				last = last[:-1]
				profesiones[-1] = last
			else:
				del profesiones[-1]
			for profession in profesiones:
				categories_dict["categories"].append(profession)
with open("classification_words.json", "w") as categories_file1:
	json.dump(categories_dict, categories_file1)

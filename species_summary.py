from pokeapi import ApiService, Species

def num_bars(width=50,progress=1.0):
	return "=" * int(width * progress)

def species_summary(species):
	MAX_STAT = 255
	stat_names = {
		'hp':"HP",
		'attack':"Attack",
		"defense":"Defense",
		'sp_atk':"Special Attack",
		'sp_def':"Special Defense",
		'speed':"Speed"
	}
	print("Species Summary for",species.name,end='\n\n')
	print("Stats Summary:")
	for stat_name in ["hp","attack","defense","sp_atk","sp_def","speed"]:
		stat = getattr(species,stat_name)
		rating = stat / MAX_STAT
		bars = num_bars(progress = rating)
		print("{:>20}:[{:50}] {}".format(stat_names[stat_name],bars,stat))
	print()

if __name__=="__main__":
	from sys import argv;argv=argv[1:]
	service = ApiService()
	for species_id in argv:
		species_id = int(species_id)
		species = Species.get_instance(service,species_id)
		species_summary(species)

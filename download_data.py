from pokeapi import ApiService

def get_id(species_stub):
	# see documentation:
	# http://pokeapi.co/docs/#pokedex
	resource_uri = species_stub['resource_uri'][len('pokemon/'):-1]
	return int(resource_uri,10)
	service = ApiService()

def pull_all_data(service,report_progress=False):
	pokedex = service.queue('pokedex/1').result()
	pokemon = sorted(pokedex.collections['pokemon'],key=get_id)
	pokedex.collections['pokemon'] = list(pokemon)
	pokedex = pokedex.preload_collection('pokemon',service).wait()
	num_species = len(pokemon)
	completed = 0
	for species in pokedex:
		percent_complete = completed / num_species
		bars = "=" * int(percent_complete*50)
		percent_complete = int(percent_complete*100)
		print("\r[{:50}]: {}%".format(bars,completed*100//num_species,percent_complete),end='')
		species.preload_collection("types",service).wait()
		species.preload_collection("moves",service).wait()
		species.preload_collection("abilities",service).wait()
		species.preload_collection("egg_groups",service).wait()
		species.preload_collection("sprites",service).wait()
		descriptions = species.preload_collection("descriptions",service).wait()
		for desc in descriptions:
			desc.preload_collection("games",service).wait()
		completed += 1
	percent_complete = completed / num_species
	bars = "=" * int(percent_complete*50)
	percent_complete = int(percent_complete*100)
	print("\r[{:50}]: {}%".format(bars,completed*100//num_species,percent_complete),end='')

if __name__=="__main__":
	welcome = """
This program will download and store all of the data
from http://pokeapi.co/ for use in a local environment.
If you use it in your own program, there is a method
called "pull_all_data" that takes a single argument,
"service" which needs to be an ApiService instance,
and an optional second keyword argument, report_progress,
which will spit out a nifty progress bar in the console.
""".strip()
	print(welcome)
	pull_all_data(ApiService(),True)

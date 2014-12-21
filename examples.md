# Download the Pokedex:
```
pokedex = ApiService().queue('pokedex/1').result()
```

# Download a species:

```
species = ApiService().queue('pokemon/1').result()
```

# Download the data for all species:

```
service = ApiService()
pokedex = ApiService.queue("pokedex/1").result()
species_list = pokedex.preload_collection('pokemon',service).wait()
```

# Using the convenience class's.
```
Species.get_instance(ApiService(),2)
```

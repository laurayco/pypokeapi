
# LookupResource
This is just a convenience / shortcut class.
It defines a class-method, get_instance(service,index)
and is a way of being more explicit when retreiving a data-resource.
the uri is calculated by cls.KIND + "/" + str(index),
and the result of service.queue(uri) is returned.
There are a few pre-defined sub-classes of this,
and they simply override the KIND class variable.
These are the pre-defined convenience classes:
* Pokedex
* Species
* Move
* Ability
* EggGroup
* Description
* Sprite
* Game
* ElementType

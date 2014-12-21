pypokeapi
=========

Python Wrapper around pokeapi.co

There are really two main classes you need to worry about:
ApiService, and ApiResource so I'll cover those first.

# ApiService
This class uses a ThreadPoolExecutor to handle retrieving
any resources used by the API. It has a cache that will
store / load from the disk, and keep them cache'd in memory.
In a sense, it's a 3-level cache:
1. Memory
2. Disk
3. Network
However, the network is handled with the ApiService class.

## queue(uri)
This adds the given resource URI to the ThreadPoolExecutor
to be retrieved from the 3-level-cache. It returns a Future
object. For more info, see the python docs.

## get_resource(uri)
This is a way to get a resource without threading, and is
the method called by the ThreadPoolExecutor function.
If the resource is not stored int level 1 or 2 of the cache
then it will be downloaded using self.download(uri)

## download(uri)
This method simply downloads the resource at the given uri.
The url is simply "http://pokeapi.co/api/v1" + uri.
If the Content-Length header is sent, progress wil be reported.
Otherwise this method is silent, and returns an ApiResource instanc.e


# ApiResource

## __init__(data)
The constructor takes a dict-object and calls self.fill(data).
The fields created are "fields", and "collections".
"fields" is a list of data-fields retrieved from the data object.
"collections" is a dict of data-fields that had a list of things.
The keys to "collections" are the names of these lists,
and the values are the data.

## fill_data(data)
This method populates the "fields", and "collections" values.
Anything that isn't a collection is placed into fields,
and anything that is a field is stored into self.__dict__
for simpler access. To separate data-fields from run-time
fields, the names of the data-fields are stored into the
"fields" member.

## preload_collection(collection,service)
This method is cool. It takes two arguments: collection and service.
collection should be a name of a data-collection ( see fill_data() )
and service should be an instance of ApiService. It creates, and returns
a Wall instance and queues all of the data items in the collection
to be retrieved from the service. When one of these resources are finished
being retrieved, the Wall object will check to see if *all* of them
have been downloaded. If they are, the Wall's .running Event will be set.
As a convenience method, you can call Wall_instance.wait() and the
current thread will wait until all resources have been retrieved,
and return the downloaded resources as a list.

## to_primitive()
This method just turns the instance into a dict that can be re-used
as an argument to the constructor and create an identical object.

# DiskCache
This class implements the __getitem__, __contains__, and __setitem__
method. It also has a limit on how many resources can be stored in
memory at a time. This class will handle string as the data type,
but it's intended to be used as a BaseClass.

## .__init__(directory,max_size=128)
The constructor simply sets the
directory and max_size of the in-memory
cache.

## .__getitem__(key)
This will first check __contains__(key). If the key is not in-memory
or on-disk, a KeyError will be raised. Otherwise, the instance
available on memory will be returned. If that is not available,
The cache will be pruned, and then the resource will be loaded from disk.

## .__setitem__(key,value)
This method will store the key/value into memory, and prune().
After it's stored in-memory, the resource will also be saved to disk.

## .save(key,value)
This method will turn key into a filename, and write into that filename.
value should be something that can be written directly to a file using
the ".write" method.

## .load(key)
This method turns key into a filename, and loads raw data from the file.
It then returns this data as raw data.

## .compile(value)
This method turns what is stored in-memory(value) into raw data.

## .decompile(data)
This method turns "data" into something you can work with. This is what
gets stored into memory.

## .make_filename(key)
This method returns self.directory + "/" + key by default.
It also strips any trailing "/" characters. Because
you can't write into a directory. That would be silly.
If you would like to add extensions to your filenames,
overriding this method is probably a good idea.

# JSONCache(DiskCache)
This class inherits from DiskCache, and uses
dict / list types as run-time instances.

## .compile(value)
Simply returns json.dump(value)

## .decompile(data)
return json.loads(data)

## .make_filename(key)
Adds the .json extension to the filename.
return super().make_filename + ".json"

# ApiResource(JSONCache)
This class takes JSON data and stores ApiResource's in memory.

## .compile(value)
value is an ApiResource instance.
Returns a JSON string representing the ApiResource.
Ultimately returns json.dumps(value.to_primitive())

## .decompile(data)
data is a JSON string, this returns an ApiResource instance.
ApiResource(json.loads(data))

# .Wall

## .touchback(future)
This removes the future instance from the list of futures
that are waiting. When this list has zero elements left,
the .running Event gets set. The value of .result() is
appended to the .received list.

## .prepare(future)
Adds the future instance to the waiting queue.

## .wait
This returns all received results after waiting for all of them
to be retreived ( when .running.wait() returns, in other words ).
If there are no results waiting to be retreived, the results are
simply returned and no call to .running.wait is made.

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

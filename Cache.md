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

# ApiCache(JSONCache)
This class takes JSON data and stores ApiResource's in memory.

## .compile(value)
value is an ApiResource instance.
Returns a JSON string representing the ApiResource.
Ultimately returns json.dumps(value.to_primitive())

## .decompile(data)
data is a JSON string, this returns an ApiResource instance.
ApiResource(json.loads(data))

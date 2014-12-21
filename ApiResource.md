
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

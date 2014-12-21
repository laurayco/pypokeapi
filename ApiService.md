
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

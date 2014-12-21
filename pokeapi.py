from functools import partial
from threading import Event, RLock as Lock
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from json import loads, dumps
from os import listdir
from os.path import exists as file_exists

# 40 Meadowbrook circle Bentonville, Arkansas

class DiskCache:
	def __init__(self,directory,max_size=128):
		self.directory = directory
		self.memcache = {}#key:{frequency,content}
		self.max_size = max_size
		self.disable_save = False
		self.save_control = Lock()
	def __contains__(self,key):
		key = self.make_filename(key)
		if key in self.memcache:
			return True
		return file_exists(key)
	def __getitem__(self,key):
		fn = self.make_filename(key)
		try:
			self.memcache[fn]['frequency'] += 1
			return self.memcache[fn]['content']
		except KeyError:
			self.prune()
			self.memcache[fn] = {
				'content':self.decompile(self.load(key)),
				'frequency':1
			}
			return self.memcache[fn]['content']
	def __setitem__(self,key,value):
		self.prune()
		fn = self.make_filename(key)
		self.memcache[fn] = {
			'content':self.decompile(value),
			'frequency':1
		}
		self.save(key,value)
	def prune(self):
		if len(self.memcache)==self.max_size:
			key_frequency = {}
			for key,val in self.memcache.items():
				key_frequency[val['frequency']] = key
			del self.memcache[key_frequency[min(key_frequency.keys())]]
	def make_filename(self,key):
		base = self.directory + "/" + key
		while base[-1] == '/':
			base = base[:-1]
		return base
	def save(self,key,value):
		with self.save_control:
			if not self.disable_save:
				fn = self.make_filename(key)
				with open(fn,'w') as f:
					f.write(value)
	def load(self,key):
		fn = self.make_filename(key)
		with open(fn) as f:
			return f.read()
	def compile(self,value):
		return value
	def decompile(self,data):
		return data

class JSONCache(DiskCache):
	def __init__(self,directory,max_size=128):
		super().__init__(directory,max_size)
	def compile(self,value):
		return dumps(value)
	def decompile(self,data):
		return loads(data)
	def make_filename(self,key):
		return super().make_filename(key) + ".json"

class APICache(JSONCache):
	def __init__(self,directory,max_size=128):
		super().__init__(directory,max_size)
	def compile(self,value):
		return super().compile(value.to_primitive())
	def decompile(self,data):
		return ApiResource(super().decompile(data))

class Wall:
	display_progress = False
	def __init__(self,datakey='resource_uri'):
		self.queued = set()
		self.received = []
		self.running = Event()
	def touchback(self,future):
		self.queued.remove(future)
		self.received.append(future.result())
		received = len(self.received)
		total = received + len(self.queued)
		if self.display_progress:
			print("{} completed of {}".format(received,total))
		if len(self.queued)<1:
			self.running.set()
	def prepare(self,future):
		self.queued.add(future)
		future.add_done_callback(self.touchback)
	def wait(self):
		if len(self.queued)>0:
			self.running.wait()
		return self.received

class ApiService:
	BASE_URL = 'http://pokeapi.co/api/v1'
	def __init__(self):
		self.executor = ThreadPoolExecutor(max_workers=3)
		self.cache = APICache('./pokeapicache')
	def queue(self,uri):
		return self.executor.submit(self.get_resource,uri)
	def download(self,uri):
		chunk_size = 256
		progress_bar_width = 20
		data = b''
		encoding = 'utf-8'
		url = self.BASE_URL + uri
		conn = urlopen(url)
		ContentLength = conn.getheader("Content-Length")
		if ContentLength:
			total_size = int(ContentLength.strip())
		while True:
			chunk = conn.read(chunk_size)
			if chunk:
				data = data + chunk
			else:
				break
			if ContentLength:
				completed = (100 * len(data)) // total_size
				bars = "=" * (progress_bar_width * completed / 100.0)
				print("[{}] - {} is {}% complete".format(bars,uri, completed))
		return data.decode(encoding)
	def get_resource(self,uri):
		try:
			return self.cache[uri]
		except Exception as e:
			self.cache[uri] = self.download(uri)
			return self.cache[uri]

class ApiResource:
	def __init__(self,data):
		self.last_modified = data['modified']
		self.created = data['created']
		self.resource_uri = data['resource_uri']
		self.collections = {}
		self.fields = []
		self.fill_data(data)
	def fill_data(self,data):
		things_that_are_lists = filter((lambda x:isinstance(x[1],list)),data.items())
		def reduce_collection_data(datatype,meta):
			resource_uri = meta['resource_uri']
			resource_uri = resource_uri[resource_uri.find("/v1/")+4:]
			r = {'resource_uri':resource_uri}
			for key,value in meta.items():
				if key!='resource_uri':
					r[key]=value
			return r
		for collection_sort, _data in things_that_are_lists:
			f = partial(reduce_collection_data,collection_sort)
			self.collections[collection_sort] = list(map(f,_data))
		for key,value in data.items():
			if key not in self.collections:
				self.__dict__[key] = value
				self.fields.append(key)
	def preload_collection(self,collection,service_handle):
		wall = Wall()
		for data_item in self.collections[collection]:
			future = service_handle.queue(data_item['resource_uri'])
			wall.prepare(future)
		return wall
	def to_primitive(self):
		r = {}
		def data_item(i):
			r = {}
			r.update(i)
			r['resource_uri'] = 'api/v1/' + r['resource_uri']
			return r
		for field in self.fields:
			r[field] = getattr(self,field)
		for key, data in self.collections.items():
			r[key] = list(map(data_item,data))
		return r

class LookupResource(ApiResource):
	KIND='pokedex'
	@classmethod
	def get_instance(cls,service,index):
		uri = cls.KIND + "/" + str(index)
		return service.queue(uri).result()

class Pokedex(LookupResource):
	@classmethod
	def get_instance(cls,service):
		LookupResource(cls,service,1)

class Species(LookupResource):
	KIND = 'pokemon'

class Move(LookupResource):
	KIND = 'move'

class Ability(LookupResource):
	KIND = 'ability'

class EggGroup(LookupResource):
	KIND = 'egg_group'

class Description(LookupResource):
	KIND = 'description'

class Sprite(LookupResource):
	KIND = 'sprite'

class Game(LookupResource):
	KIND = 'game'

class ElementType(LookupResource):
	KIND = 'type'

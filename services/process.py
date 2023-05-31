from hashlib import sha256
from urllib import request
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from os import remove
from io import BufferedReader

class Process():
    def __init__(self) -> None:
        self.images = dict()
        self

    def __sha_from_reader(self, file):
        hash = sha256()
        for chunk in iter(lambda: file.read(4096), b""):
            hash.update(chunk)
        return hash.hexdigest()
    
    def add_image_from_buffer(self, name, buffer):
        with NamedTemporaryFile(delete=False) as tmp_file:
            copyfileobj(buffer, tmp_file)
            tmp_file.seek(0) # Reset tmp_file pos
            hash = self.__sha_from_reader(tmp_file)
            tmp_file.seek(0) # Reset tmp_file pos
            if self.images.get(hash) != None:
                remove(tmp_file.name)
            else:
                self.images[hash] = (name, tmp_file.name)

    def add_image_from_url(self, url):
        with request.urlopen(url) as response:
            self.add_image_from_buffer(url.rsplit('/', 1)[-1], response)

    def get_images(self):
        return list(map(lambda k: [self.images.get(k)[0], k, self.images.get(k)[1]], self.images.keys()))
    
    def get_image(self, hash):
        return open(self.images.get(hash)[1], "rb")
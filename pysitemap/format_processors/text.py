import os
from aiofile import AIOFile, Reader, Writer


class TextWriter:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dir, self.filename = os.path.split(self.filepath)

    async def write(self, urls):
        if self.dir and not os.path.exists(self.dir):
            os.makedirs(self.dir)

        async with AIOFile(self.filepath, "w") as aiodf:
            writer = Writer(aiodf)

            for url in urls:
                await writer("{}\n".format(url))
            await aiodf.fsync()

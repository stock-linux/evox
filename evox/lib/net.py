import sys, os, shutil
from urllib import request
import lib.log as log

def download(link, file_name, dl_log=True):
    if os.path.exists(link):
        if os.path.exists(file_name):
            if not os.path.samefile(link, file_name):
                shutil.copyfile(link, file_name)
        else:
            shutil.copyfile(link, file_name)
        return True

    with open(file_name, "wb") as f:
        if dl_log:
            log.log_info("Downloading " + link + "...")
        
        response = request.urlopen(link)
        meta = response.info()
        file_size = int(meta["Content-Length"])
        file_size_dl = 0
        block_sz = 4096

        while True:
            buffer = response.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

            if dl_log:
                bar = "["
                bar_size = 25
                bar_progress = int(file_size_dl / file_size * bar_size)
                bar += "#" * bar_progress
                bar += "-" * (bar_size - bar_progress)
                bar += "]"

                percent = int(file_size_dl / file_size * 100)

                sys.stdout.write("\r" + bar + " " + str(percent) + "%")

    if dl_log:
        print()
        log.log_success("Done!")
        print()
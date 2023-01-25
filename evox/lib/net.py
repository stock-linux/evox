import sys, requests, os, shutil

import lib.log as log

def download(link, file_name, dl_log=True):
    if os.path.exists(link):
        if os.path.exists(file_name) and not os.path.samefile(link, file_name):
            shutil.copyfile(link, file_name)
        return

    with open(file_name, "wb") as f:
        if dl_log:
            log.log_info("Downloading " + link + "...")
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                if dl_log:
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                    sys.stdout.flush()
    if dl_log:
        print()
        log.log_success("Done!")
        print()
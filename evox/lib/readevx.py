import zstandard as zstd
import tarfile
import tempfile
import os

def readevx(filename, package):
    """Reads an eVox file and returns the data as a dictionary.
    """
    # The eVox file is a .tar.zst archive, so we need to open it as such.
    # tarfile cannot open .tar.zst files, so we need to use the zstandard library.
    # We open the file in read mode

    pkginfo_dict = {}

    with open(filename, "rb") as f:
        # We create a decompressor object
        dctx = zstd.ZstdDecompressor()
        # We create a reader object
        reader = dctx.stream_reader(f)
        # We need to write the data to a tar file
        open("temp.tar", "w").close()
        open("temp.tar", "wb").write(reader.read())

        with tarfile.open("temp.tar", "r") as tar:
            # The eVox archive has the following structure:
            # - metadata/
            #  - PKGINFO
            #  - PKGDEPS
            #  - PKGTREE
            # - data/
            #   - <files>
            # - scripts/
            #   - <scripts>

            # We need to extract the PKGINFO file to get the package infos.
            # The PKGINFO has the following needed fields:
            # - name
            # - version
            # - description
            # - source
            # - pkgrel
            # And the following optional fields:
            # - url
            # - license
            # - maintainer
            
            # Extract the PKGINFO file
            pkginfo = tar.extractfile(package + "/metadata/PKGINFO").read().decode("utf-8")
            # Split the PKGINFO file into lines
            pkginfo = pkginfo.splitlines()
            # Create a dictionary to store the package infos
            # Loop through the lines
            for line in pkginfo:
                # Split the line into key and value
                key, value = line.split(" = ")
                # Add the key and value to the dictionary
                pkginfo_dict[key] = value

            # We check that the needed fields are present
            if "name" not in pkginfo_dict:
                raise Exception("Package name not found in PKGINFO")
            if "version" not in pkginfo_dict:
                raise Exception("Package version not found in PKGINFO")
            if "description" not in pkginfo_dict:
                raise Exception("Package description not found in PKGINFO")
            if "source" not in pkginfo_dict:
                raise Exception("Package source not found in PKGINFO")
            #if "pkgrel" not in pkginfo_dict:
            #    raise Exception("Package release (pkgrel field) not found in PKGINFO")
            
            # We need to extract the PKGDEPS file to get the package dependencies.
            # The PKGDEPS file has the following structure:
            # - <package name>
            # - <package name>
            # - <package name>
            # - ...

            # Note that the package dependencies are optional, so we need to check if the file exists.
            if package + "/metadata/PKGDEPS" in tar.getnames():
                # Extract the PKGDEPS file
                pkgdeps = tar.extractfile(package + "/metadata/PKGDEPS").read().decode("utf-8")
                # Split the PKGDEPS file into lines
                pkgdeps = pkgdeps.splitlines()
                # Create a list to store the package dependencies
                pkgdeps_list = []
                # Loop through the lines
                for line in pkgdeps:
                    # Add the line to the list
                    pkgdeps_list.append(line)

                # We add the package dependencies to the package infos dictionary
                pkginfo_dict["depends"] = pkgdeps_list

        # Delete the temp.tar file
        os.remove("temp.tar")
        # We return the package infos dictionary
        return pkginfo_dict
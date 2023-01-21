import os

if not "ROOT" in os.environ:
        root = "/"
else:
    root = os.environ["ROOT"]
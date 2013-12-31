import os

def getOpenFilename(default = None):
    """
    Prompts the user to pick a file name.  If the user doesn't enter a filename,
    returns the default.
    """

    prompt = "Enter a file name to load from"
    if default is not None:
        prompt += (" (default: %s)" % default)
    prompt += ": "

    filename = raw_input(prompt)
    if filename == "" and not (default is None):
        filename = default

    return filename

def getSaveFilename(default = None):
    """
    Prompts the user to pick a file name.  If the user doesn't enter a filename,
    returns the default.  If the file already exists, checks to make sure that
    the user wants to overwrite it.
    """

    prompt = "Enter a file name to save to"
    if default is not None:
        prompt += (" (default: %s)" % default)
    prompt += ": "

    filename = raw_input(prompt)
    if filename == "" and not (default is None):
        filename = default

    if os.path.exists(filename):
        print("The file %s already exists." % filename)
        prompt = ("Overwrite (o), enter another name (f), or cancel (c)? ")
        
        check = raw_input(prompt)
        while (check != "o" and check != "f" and check != "c"):
            check = raw_input(prompt)

        if check == "o":
            return filename
        elif check == "f":
            return getSaveFilename(default)
        elif check == "c":
            return None

    return filename

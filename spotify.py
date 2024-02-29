from SwSpotify import spotify

def isplaying():
    try:
        spotify.current()
    except:
        return False
    return True

def current():
    try:
        return spotify.current()
    except:
        return (False, False)
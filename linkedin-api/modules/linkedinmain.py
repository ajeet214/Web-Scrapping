import sys

from modules import linkedinprofile

import linkedinsearch


def lmain(*kwargs):

    try:
        if len(kwargs) == 2:
            if kwargs[1].isnumeric():
                return linkedinsearch.profilesearch(name=kwargs[0], page=kwargs[1])
        elif len(kwargs) == 1:
            if "https" in kwargs[0]:
                k = linkedinprofile.ProfileFetcher()
                return k.Porfile(url=kwargs[0])
            else:
                raise Exception
        else:
            raise Exception

    except Exception :
        print("error>>found::", sys.exc_info()[1])

if __name__ == '__main__':
    print(lmain("mark", "2"))
    # print(lmain("https://www.linkedinProject.com/in/bobprince1/"))

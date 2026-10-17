import os
'''Path to Record Book Data'''
sitepath = '/home/buhockeystats/mysite/recordbookdata/'

if os.path.isdir(sitepath):
    RECBOOK_DATA_PATH = sitepath

else:
  RECBOOK_DATA_PATH = f'{os.getcwd()}/recordbookdata/'

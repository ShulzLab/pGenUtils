import os,sys

_localpath = os.path.dirname(os.getcwd())
_packages_path = os.path.dirname(_localpath)

print(_packages_path)
sys.path.append(_packages_path)

from pGenUtils.docs import mkds_make_docfiles  

mkds_make_docfiles(_localpath)
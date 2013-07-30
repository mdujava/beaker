import errno
import logging
import os.path
from turbogears import config
from lxml import etree
import logging
log = logging.getLogger(__name__)

# The MOTD is loaded once and cached globally. Admins need to restart the 
# application (or wait for it to be recycled by mod_wsgi) when updating 
# the MOTD.
_motd_loaded = False
_motd = None

def _load_motd(filename):
    try:
        f = open(filename, 'rb')
    except IOError, e:
        if e.errno == errno.ENOENT:
            log.info('Motd not found at %s, ignoring', filename)
            return None
        else:
            raise
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(f,parser)
    if tree.getroot() is None:
        return None
    return etree.tostring(tree.getroot())

def get_motd():
    global _motd, _motd_loaded
    if not _motd_loaded:
        try:
            _motd = _load_motd(config.get('beaker.motd', '/etc/beaker/motd.xml'))
        except Exception:
            log.exception('Unable to read motd')
        _motd_loaded = True
    return _motd

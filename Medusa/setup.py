from setuptools import setup, find_packages
from turbogears.finddata import find_package_data
import glob
import re
import os
from distutils.dep_util import newer
from distutils import log

from distutils.command.build_scripts import build_scripts as _build_scripts
from distutils.command.build import build as _build
from distutils.command.install_data import install_data as _install_data
from distutils.dep_util import newer
from setuptools.command.install import install as _install
from setuptools.command.install_lib import install_lib as _install_lib
from turbogears.finddata import find_package_data, standard_exclude, \
        standard_exclude_directories
execfile(os.path.join("medusa", "release.py"))

excludeFiles = ['*.cfg.in']
excludeFiles.extend(standard_exclude)
excludeDataDirs = ['medusa/static', 'comps']
excludeDataDirs.extend(standard_exclude_directories)

poFiles = filter(os.path.isfile, glob.glob('po/*.po'))

SUBSTFILES = ('medusa/config/app.cfg')

class Build(_build, object):
    '''
    Build the package, changing the directories that data files are installed.
    '''
    user_options = _build.user_options
    user_options.extend([('install-data=', None,
        'Installation directory for data files')])
    # These are set in finalize_options()
    substitutions = {'@DATADIR@': None, '@LOCALEDIR@': None}
    subRE = re.compile('(' + '|'.join(substitutions.keys()) + ')+')

    def initialize_options(self):
        self.install_data = None
        super(Build, self).initialize_options()
    def finalize_options(self):
        if self.install_data:
            self.substitutions['@DATADIR@'] = self.install_data + '/medusa'
            self.substitutions['@LOCALEDIR@'] = self.install_data + '/locale'
        else:
            self.substitutions['@DATADIR@'] = '%(top_level_dir)s'
            self.substitutions['@LOCALEDIR@'] = '%(top_level_dir)s/../locale'
        super(Build, self).finalize_options()

    def run(self):
        '''Substitute special variables for our installation locations.'''
        for filename in SUBSTFILES:
            # Change files to reference the data directory in the proper
            # location
            infile = filename + '.in'
            if not os.path.exists(infile):
                continue
            try:
                f = file(infile, 'r')
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            outf = file(filename, 'w')
            for line in f.readlines():
                matches = self.subRE.search(line)
                if matches:
                    for pattern in self.substitutions:
                        line = line.replace(pattern,
                                            self.substitutions[pattern])
                outf.writelines(line)
            outf.close()
            f.close()

        # Make empty en.po
        dirname = 'locale/'
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        #shutil.copy('po/LINGUAS', 'locale/')

        for pofile in poFiles:
            # Compile PO files
            lang = os.path.basename(pofile).rsplit('.', 1)[0]
            dirname = 'locale/%s/LC_MESSAGES/' % lang
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            # Hardcoded gettext domain: 'medusa'
            mofile = dirname + 'medusa' + '.mo'
            subprocess.call(['/usr/bin/msgfmt', pofile, '-o', mofile])
        super(Build, self).run()

class InstallData(_install_data, object):

    def finalize_options(self):
        '''Override to emulate setuptools in the default case.
        install_data => install_dir
        '''
        self.temp_lib = None
        self.temp_data = None
        self.temp_prefix = None
        haveInstallDir = self.install_dir
        self.set_undefined_options('install',
                ('install_data', 'temp_data'),
                ('install_lib', 'temp_lib'),
                ('prefix', 'temp_prefix'),
                ('root', 'root'),
                ('force', 'force'),
                )
        if not self.install_dir:
            if self.temp_data == self.root + self.temp_prefix:
                self.install_dir = os.path.join(self.temp_lib, 'medusa')
            else:
                self.install_dir = self.temp_data

data_files = [
    ('medusa/static', filter(os.path.isfile, glob.glob('medusa/static/*'))),
    ('medusa/static/css', filter(os.path.isfile,
                                 glob.glob('medusa/static/css/*'))),
    ('medusa/static/javascript', filter(os.path.isfile,
                                 glob.glob('medusa/static/javascript/*'))),
    ('medusa/static/images', filter(os.path.isfile,
                                 glob.glob('medusa/static/images/*'))),
    ("/etc/medusa", ["medusa.cfg"]),
    ("/etc/cron.daily", ["lab-controller/cron.daily/expire_distros"]),
    ("/etc/httpd/conf.d", ["apache/medusa.conf", "lab-controller/conf.d/beaker.conf"]),
    ("/var/lib/cobbler/triggers/sync/post", filter(os.path.isfile, glob.glob("lab-controller/triggers/sync/post/*"))),
    ("/var/lib/cobbler/triggers/install/pre", filter(os.path.isfile, glob.glob("lab-controller/triggers/install/pre/*"))),
    ("/var/lib/cobbler/kickstarts", filter(os.path.isfile, glob.glob("lab-controller/kickstarts/*"))),
    ("/var/lib/cobbler/snippets", filter(os.path.isfile, glob.glob("lab-controller/snippets/*"))),
    ("/usr/share/medusa", filter(os.path.isfile, glob.glob("apache/*.wsgi"))),
    ("/var/www/beaker", ["lab-controller/aux/rhts-checkin"]),
    ("/var/log/medusa", []),
    ("/var/lib/medusa", []),
    ("/var/lib/cobbler/snippets/per_system/Fedora", []),
    ("/var/lib/cobbler/snippets/per_system/Fedora_pre", []),
    ("/var/lib/cobbler/snippets/per_system/Fedora_post", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinux3", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinux3_pre", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinux3_post", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinux4", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinux4_pre", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinux4_post", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinuxClient5", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinuxClient5_pre", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinuxClient5_post", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinuxServer5", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinuxServer5_pre", []),
    ("/var/lib/cobbler/snippets/per_system/RedHatEnterpriseLinuxServer5_post", []),
]

packages=find_packages()
package_data = find_package_data(where='medusa',
                                 package='medusa',
                                 exclude=excludeFiles,
                                 exclude_directories=excludeDataDirs)
package_data['medusa.config'].append('app.cfg')

if os.path.isdir('locales'):
    packages.append('locales')
    package_data.update(find_package_data(where='locales',
        exclude=('*.po',), only_in_packages=False))

setup(
    name="medusa",
    version='0.2',

    # uncomment the following lines if you fill them out in release.py
    description=description,
    author=author,
    author_email=email,
    url=url,
    #download_url=download_url,
    license=license,
    cmdclass = {
        'build': Build,
        'install_data': InstallData,
    },
    install_requires=[
        "TurboGears >= 1.0.3.2",
    ],
    scripts=[],
    zip_safe=False,
    data_files = data_files,
    packages = find_packages(),
    package_data = package_data,
    keywords=[
        'turbogears.app',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Applications',
    ],
    test_suite='nose.collector',
    entry_points = {
        'turbogears.identity.provider': (
            'ldapsa = medusa.identity:LdapSqlAlchemyIdentityProvider'
        ),
        'console_scripts': (
            'start-medusa = medusa.commands:start',
            'medusa-init = medusa.tools.init:main',
        ),
    }
    )


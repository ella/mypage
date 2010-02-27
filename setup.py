from setuptools import setup, find_packages

# must be in sync with mypage.VERSION
VERSION = (0, 5, 0, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))


setup(
    name = 'mypage',
    version = __versionstr__,
    description = 'django mypage project',
    long_description = '\n'.join((
        'django mypage project',
        '',
        'user customizing pages',
    )),
    author = 'centrum holdings s.r.o',
    author_email='pg-content-dev@chconf.com',
    license = 'BSD',
    url='http://github.com/ella/mypage',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),
    include_package_data = True,

    buildbot_meta_master = {
        'host' : 'cnt-buildmaster.dev.chservices.cz',
        'port' : 10001,
        'branch' : 'automation',
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires = [
#        'django',
#        'simplejson',
#        'lxml',
        'setuptools>=0.6b1',
    ],
    setup_requires = [
        'setuptools_dummy',
    ],
)


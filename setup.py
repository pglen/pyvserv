import sys, os
import setuptools

descx = '''
        pyvserv is modern multi-process data server.
        '''

classx = [
          'Development Status :: Mature',
          'Environment :: GUI',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Servers',
        ]

includex = ["*", "pyvgui/", "pyvgui/guilib/", "pyvclient/", "pyvserver/",
                    "pyvcommon/", "pyvtools/", ]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# The shortlist of starter applications

test_root = [\
    "pyvcli_cli",
    "pyvcli_gethelp",
    "pyvcli_ver",
    "pyvcli_hello",
    "pyvcli_uini",
    "pyvcli_uman",
    "pyvcli_fman",
    "pyvcli_rman",
    "pyvcli_qr",
    "pyvcli_ihost",
    "pyvcli_replic",
    ]

# Generate script and loadable details
test_scripts = []; test_exec = []
for aa in test_root:
    test_scripts.append("pyvclient/" + aa + ".py")
    test_exec.append(aa+"="+aa+":mainfunct")

#print(test_scripts); #print(test_exec)

# Get version number  from the server support file:
fp = open("pyvcommon/pyservsup.py", "rt")
vvv = fp.read(); fp.close()
loc_vers =  '1.0.0'     # Default
for aa in vvv.split("\n"):
    idx = aa.find("version =")
    if idx == 0:        # At the beginning of line
        try:
            loc_vers = aa.split()[2].replace('"', "")
            break
        except:
            pass
#print("loc_vers:", loc_vers)

# Dependency list, generate separate for windows
# Sat 06.Apr.2024 same for all
try:
    import fcntl
    #deplist = ["pyvpacker", "pydbase", "pycryptodome",
    #                    "pyvecc", "pyvguicom", "readline"],

    # Thu 04.Apr.2024 abandoned readline; may install by hand
    deplist = ["pyvpacker", "pydbase", "pycryptodome",
                        "pyvecc", "pyvguicom", ],
except:
    # No fnctl, windows
    deplist = ["pyvpacker", "pydbase", "pycryptodome",
                        "pyvecc", "pyvguicom"],

doclist = []; droot = "pyvserver/docs/"
doclistx = os.listdir(droot)
for aa in doclistx:
    doclist.append("docs/" + aa)

cdoclist = []; droot2 = "pyvclient/docs/"
cdoclistx = os.listdir(droot2)
for aa in cdoclistx:
    cdoclist.append("docs/" + aa)

tdoclist = []; droot3 = "pyvtools/docs/"
tdoclistx = os.listdir(droot3)
for aa in tdoclistx:
    tdoclist.append("docs/" + aa)

# This was needed to verify lists ...
#print("includex:", includex)
#print("find packages:", setuptools.find_packages(include=includex))
#print("deplist:", deplist)
#print("doclist:", doclist)
#print("cdoclist:", cdoclist)
#print("tdoclist:", tdoclist)
#sys.exit(1)

setuptools.setup(
    name="pyvserv",
    version=loc_vers,
    author="Peter Glen",
    author_email="peterglen99@gmail.com",
    description="High power secure server with blockchain backend.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pglen/pyvserv",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=includex),
    include_package_data = True,
    scripts = [
                "pyvserver/pyvserv.py",
                "pyvserver/pyvreplic.py",
                "pyvtools/pyvgenkey.py", "pyvtools/pyvgenkeys.py",
                "pyvgui/pyvservui.py", "pyvgui/pyvcpanel.py",
                "pyvgui/pyvtally.py",
                *test_scripts,
                ],
    package_dir = {
                    'pyvgui':           'pyvgui',
                    'pyvgui/guilib':    'pyvgui/guilib',
                    'pyvcommon':        'pyvcommon',
                    'pyvserver':        'pyvserver',
                    'pyvclient':        'pyvclient',
                    'pyvtools':         'pyvtools',
                   },

    package_data = {    "pyvserver" :  doclist,
                        "pyvclient" : cdoclist,
                        "pyvtools"  : tdoclist,
                   },
    python_requires='>=3',
    install_requires=deplist,
    entry_points={
        'console_scripts': [ "pyvserv=pyvserv:mainfunct",
                             "pyvreplic=pyvreplic:mainfunct",
                             "pyvgenkey=pyvgenkey:mainfunct",
                             "pyvgenkeys=pyvgenkeys:mainfunct",
                             "pyvservui=pyvservui:mainfunct",
                             "pyvcpanel=pyvcpanel:mainfunct",
                             "pyvtally=pyvtally:mainfunct",
                             test_exec,
            ],
    },
)

# EOF

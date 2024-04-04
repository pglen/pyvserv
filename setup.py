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
          'Topic :: Editors',
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
"pyvcli_hello",
"pyvcli_rget",
"pyvcli_rlist",
"pyvcli_rput",
"pyvcli_uini",
"pyvcli_uman",
"pyvcli_qr",
]

# Generate script details

test_scripts = []
for aa in test_root:
    test_scripts.append("pyvclient/" + aa + ".py")
#print(test_scripts)

test_exec = []
for aa in test_root:
    test_exec.append(aa+"="+aa+":mainfunct")
#print(test_exec)

# Get it from main file:
fp = open("pyvserver/pyvserv.py", "rt")
vvv = fp.read(); fp.close()
loc_vers =  '1.0.0'     # Default
for aa in vvv.split("\n"):
    idx = aa.find("version =")
    if idx == 0:        # At th beginning of line
        try:
            loc_vers = aa.split()[2].replace('"', "")
            break
        except:
            pass
#print("loc_vers:", loc_vers)

# Dependency list, generate for windows
try:
    import fcntl
    #deplist = ["pyvpacker", "pydbase", "pycryptodome",
    #                    "pyvecc", "pyvguicom", "readline"],

    # Thu 04.Apr.2024 abandoned readline; may install by hand
    deplist = ["pyvpacker", "pydbase", "pycryptodome",
                        "pyvecc", "pyvguicom", ],
except:
    deplist = ["pyvpacker", "pydbase", "pycryptodome",
                        "pyvecc", "pyvguicom"],

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
    include_package_data=True,
    packages=setuptools.find_packages(include=includex),

    scripts = [
                "pyvserver/pyvserv.py",
                "pyvserver/pyvreplic.py",
                "pyvserver/pyvpuller.py",
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
                             "pyvpuller=pyvpuller:mainfunct",
                             test_exec,
            ],
    },
)

# EOF

import io

from setuptools import setup

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

VERSION = '0.1.0'
PACKAGE = 'edgePy'
AUTHOR = 'r-bioinformatics'
ARTIFACT = f'https://github.com/{AUTHOR}/{PACKAGE}/archive/v{VERSION}.tar.gz'

DESCRIPTION = """
A Python implementation of edgeR for differential expression analysis.
"""

setup(
    name=PACKAGE,
    packages=[PACKAGE],
    version=VERSION,
    description=(DESCRIPTION),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email='example@example.com',
    download_url=ARTIFACT,
    url=f'https://github.com/{AUTHOR}/{PACKAGE}',
    py_modules=[PACKAGE],
    install_requires=[],
    extras_require={
        'ci': ['nose', 'codecov'],
    },
    scripts=[
        # "scripts/edgePy",  # TODO: Uncomment to install / test script.
    ],
    package_dir={'edgePy': 'edgePy'},
    package_data={
        'edgePy': [
            'data/*.csv*',
            'data/*.tsv*',
            'data/*.txt*',
        ]
    },
    license='GPLv3',
    zip_safe=True,
    keywords='bioinformatics gene differential expression edgeR',
    project_urls={
        'Slack Group': 'https://r-bioinformatics.slack.com/',
        'Subreddit': 'https://reddit.com/r/bioinformatics/'
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)

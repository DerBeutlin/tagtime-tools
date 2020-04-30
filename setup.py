from setuptools import setup
setup(
    name = "tagtime-tools",
    version = "0.0.1",
    author = "Max Beutelspacher",
    author_email = "max@beutelspacher.eu",
    description = ("A tool to deal with logs from TagTime."),
    license = "BSD",
    keywords = "tagtime",
    url = "https://github.com/DerBeutlin/tagtime-tools",
    packages=['tagtime'],
    scripts = [
        'scripts/check.py',
        'scripts/import.py',
        'scripts/merge.py',
        'scripts/plot.py',
        'scripts/rules.py',
        'scripts/sync.py',
    ]
)

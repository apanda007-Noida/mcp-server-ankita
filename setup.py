from setuptools import setup, find_packages

setup(
    name="pulse",
    version="0.1.0",
    description="Automated Weekly App Review Pulse",
    packages=find_packages(),
    install_requires=[
        "google-play-scraper==1.2.4",
        "python-dateutil==2.8.2",
        "emoji==2.12.1",
        "langdetect==1.0.9",
    ],
    entry_points={
        "console_scripts": [
            "pulse=pulse.cli:main",
        ],
    },
)

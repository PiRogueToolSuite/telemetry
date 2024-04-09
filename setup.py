from setuptools import find_packages, setup

requirements = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name="pts-telemetry",
    version="1.0.0",
    author="U+039b",
    author_email="hello@pts-project.org",
    description="PTS privacy preserving telemetry",
    url="https://github.com/PiRogueToolSuite/pts-telemetry",
    install_requires=requirements,
    packages=find_packages(),
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "pirogue-telemetry = pts_telemetry.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
)

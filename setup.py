from setuptools import setup, find_packages
from setuptools import Command
import subprocess
import sys
import os
long_description = open("README.md").read()
VERSION = eval(os.getenv('VERSION', '"2.17.0"'))


def run(cmd, check=True):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result.returncode == 0


class PublishCommand(Command):
    description = "构建whl并上传到testpypi，然后git commit"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        # 上传
        run(["python", "-m", "twine", "upload", "--verbose", "--disable-progress-bar",
            "--repository", "testpypi", "--skip-existing", "dist/*", ])


setup(
    name="gaskill",
    version=VERSION,
    author="Limo",
    author_email="28009663@qq.com",
    description="A comprehensive Python library for game development utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/limo1027/gaskill",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    cmdclass={"publish": PublishCommand},
)

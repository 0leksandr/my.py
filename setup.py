from __future__ import annotations
import setuptools
import versioneer

setuptools.setup(name="my",
                 version=versioneer.get_version(),
                 cmdclass=versioneer.get_cmdclass())

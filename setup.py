import setuptools


setuptools.setup(
    name='mkdocs-monorepo-plugin',
    version='1.0.3',
    description='Plugin for adding monorepository support in Mkdocs.',
    long_description="""
        This introduces support for the !include syntax in mkdocs.yml, allowing you to import additional Mkdocs navigation.
        It enables large or complex repositories to have their own sets of docs/ folders, whilst generating only a single Mkdocs site.
        This is built and maintained by the engineering community at Spotify.
    """,  # noqa: E501
    keywords='mkdocs monorepo',
    url='https://github.com/backstage/mkdocs-monorepo-plugin',
    author='Bilawal Hameed',
    author_email='bil@spotify.com',
    license='Apache-2.0',
    python_requires='>=3',
    install_requires=[
        'mkdocs>=1.0.4',
        'python-slugify>=4.0.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'mkdocs.plugins': [
            "monorepo = mkdocs_monorepo_plugin.plugin:MonorepoPlugin"
        ]
    }
)

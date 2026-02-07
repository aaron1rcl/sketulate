from setuptools import setup, find_packages

setup(
    name='sketulate',
    version='1.0',
    author='Aaron Pickering',
    author_email='aaron_rcl@hotmail.com',
    description='Sketchable function and density simulations for data science',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aaron1rcl/sketulate',
    packages=find_packages(),
    python_requires='>=3.11.0',
    install_requires=[
        'numpy>=2.0.0',
	'ipywidgets>=8.0.0',
	'ipycanvas',
        'matplotlib',
        'scipy',
        'plotly',
	'scikit-learn',
	'jupyter>=7.0.5',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


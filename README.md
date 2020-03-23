[![Build Status](https://travis-ci.org/ladybug-tools/honeybee-grasshopper-energy.svg?branch=master)](https://travis-ci.org/ladybug-tools/honeybee-grasshopper-energy)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# honeybee-grasshopper-energy
:honeybee: :green_book: :fire: Honeybee Energy plugin for Grasshopper (aka. honeybee[+]).

This repository contains all energy modeling Grasshopper components for the honeybee
plugin. The package includes both the userobjects (`.ghuser`) and the Python
source (`.py`). Note that this library only possesses the Grasshopper components
and, in order to run the plugin, the core libraries must be installed (see dependencies).

# Dependencies
The honeybee-grasshopper-energy plugin has the following dependencies on core libraries:

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-dotnet](https://github.com/ladybug-tools/ladybug-dotnet)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)
* [honeybee-energy](https://github.com/ladybug-tools/honeybee-energy)
* [honeybee-energy-standards](https://github.com/ladybug-tools/honeybee-energy-standards)

# Oher Required Components
The honeybee-grasshopper-energy plugin also requires the Grasshopper components within the
following repositories to be installed in order to work correctly:

* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)
* [honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core)

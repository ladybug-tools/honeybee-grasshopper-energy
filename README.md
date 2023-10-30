[![Build Status](https://travis-ci.com/ladybug-tools/honeybee-grasshopper-energy.svg?branch=master)](https://travis-ci.com/ladybug-tools/honeybee-grasshopper-energy)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# honeybee-grasshopper-energy

:honeybee: :green_book: :fire: Honeybee Energy plugin for Grasshopper (aka. honeybee[+]).

This repository contains all energy modeling Grasshopper components for the honeybee
plugin. The package includes both the userobjects (`.ghuser`) and the Python
source (`.py`). Note that this library only possesses the Grasshopper components
and, in order to run the plugin, the core libraries must be installed in a way that
they can be found by Rhino (see dependencies).

## Dependencies

The honeybee-grasshopper-energy plugin has the following dependencies on core libraries:

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-geometry-polyskel](https://github.com/ladybug-tools/ladybug-geometry-polyskel)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)
* [ladybug-display](https://github.com/ladybug-tools/ladybug-display)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)
* [honeybee-energy](https://github.com/ladybug-tools/honeybee-energy)
* [honeybee-standards](https://github.com/ladybug-tools/honeybee-standards)
* [honeybee-energy-standards](https://github.com/ladybug-tools/honeybee-energy-standards)

## Other Required Components

The honeybee-grasshopper-energy plugin also requires the Grasshopper components within the
following repositories to be installed in order to work correctly:

* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)
* [honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core)

## Installation

See the [Wiki of the lbt-grasshopper repository](https://github.com/ladybug-tools/lbt-grasshopper/wiki)
for the installation instructions for the entire Ladybug Tools Grasshopper plugin
(including this repository).

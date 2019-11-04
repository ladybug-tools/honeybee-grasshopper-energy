# honeybee-grasshopper-plugin
:honeybee: :green_book: :fire: Honeybee Energy plugin for Grasshopper (aka. honeybee[+]).

This repository contains all energy modeling Grasshopper components for the honeybee
plugin. The package includes both the userobjects (`.ghuser`) and the Python
source (`.py`). Note that this library only possesses the Grasshopper components
and, in order to run the plugin, the core libraries must be installed to the
Rhino `scripts` folder (see dependencies).

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
[honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core)
repository to be installed in order to work correctly.

# Installation
To install the most recent version of the Grasshopper plugin, follow these steps:

1. Clone [honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core) repository to your machine.
2. Open the installer.gh in Grasshopper and set the toggle inside to `True`.
3. Restart Rhino + Grasshopper.

Note that following these steps will install the absolute most recent version of
the plugin. To install the last stable release, download the components and Grasshopper
file installer from [food4rhino](https://www.food4rhino.com/app/ladybug-tools).

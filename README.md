# pdssp-labtools
Python tools for PDSSP laboratories data services setup and maintenance.

status: _in development_

This repository is used to prototype a **"Planetary STAC Builder"**, whose the main features should be:

- Build (and update) a STAC catalog of planetary geospatial datasets from multiple local and/or remote data sources.
- Define the STAC catalog structure and content using human-friendly YAML files and directories hierarchy.
- Easily extend source metadata extraction and transformation capabilities.

Note: Such a "Planetary STAC Builder" re-uses and extend concepts from the developing [pdssp-crawler](https://github.com/pdssp/pdssp-crawler). Eventually, the latter should incorporate design elements and code from this repository.
\## V0.6 - Expansionism

\### Added:

* Improvements to the manual and preset input system in the terminal.
* Massive expansion of the rockets library.
* Entirely new metric - HEQ, based off the new integral calculations.
* Selected rocket names to the relevant graphs, and to the terminal.
* Generic .gitignore file that should cover all the bases.



\### Changed:

* Completely removed /Example Scripts as the purpose of it is now defunct.
* Completely removed PEQ/NPEQ metrics, as they have been made redundant.
* Changed MIPEQ metric into the LEQ metric, for better understanding and readability.
* Added \*some\* sources to the rockets.txt lookup table.
* Changed some things around in the terminal and fixed a few minor printing issues
* Completely rewrote README.md for the new metrics, as well as to make it easier to read and understand
* Removed sub-orbital parameters from trajectory\_targets as sub-orbital trajectories are incompatible with the integral calculations for HEQ.



\### Notes:

rockets.json is subject to being reworked in the future, any custom additions of it will need porting to the new system, thus it is highly

recommended you utilise the rockets.txt lookup table to store the relevant information for later porting.





\## V0.5 - A New Input

\### Added

* Terminal based input system created
* Support for manual input for booster-less rockets
* Initial groundwork started for JSON based presets
* Updated README.md



\### Notes:
Subsequent updates will NOT include /Example Scripts, this was a placeholder for the json presets before it existed, therefore it will be made redundant with the expansion of rockets.json.









\## V0.4

Initial GitHub Release


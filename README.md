# ParametricSimulationForHospitality

## Introduction
* This script could run EnergyPlus parametrically with Eppy package( [Eppy tutorial link](https://pythonhosted.org/eppy/Main_Tutorial.html)), and generating new IDF files.
* This script is used to analyze the peak load for hospitality unit model which could help analyze the practical HVAC sizes 
* This script could change the construction materials for window, grade slab and wall, then ran the simulation for four orientations: 0, 90, 180, 270
* This script used multipliers for middle units and corner units by 15 and 4 to offset the bias
* This script read the zone component load summary report and output the peak loads to a csv file, adding the "Zone Component Load Summary Report" is written into the scripts, so no need to add this before simulation
* The cities to simulate could be listed in the "WeatherFileNameList.csv" to help pick up the weather files, but they should be downloaded before simulation. Link to EnergyPlus weather website: [Click Here](https://energyplus.net/weather), Scripts to download all the epw and ddy files: [Click Here](https://gist.github.com/aahoo/b4aaeb179b51b69e342c5e324e305155)
* This script automatically read the files from the IDF folder, 

### Variables and Paths
* At least one initial IDF model is needed for running this parametric simulation
* The path to the directory where stores IDF , weather file name csv file and weather files should be clarified
* An idd file is required to run the simulation with EnergyPlus engine

### Functions
* The functions in this project is similar to those in [EppyEnergyPlus](https://github.com/yzhou601/EppyEnergyPlus)
import csv
import os
import re
from typing import List, Any
import pandas as pd
from eppy.modeleditor import IDF
from eppy.results import readhtml
import pprint


##pack the file into blocks
def packddy(ddypath):
    '''
    This function helps pack up ddy files into blocks by recognizing blank lines as separations
    :param ddypath: This is the path to the directory where the ddy files are located
    :return: This function returns the lists of blocks which are lists of lines in ddy files
    '''
    start = ['  \n', ' \n', '\n']
    my_list = []    ##temporary list
    packedls = []   ##final packed list with blocks
    for line in open(ddypath,'rt').readlines():
        if line.startswith(start[0]) or line.startswith(start[1]) or line.startswith(start[2]):
            packedls.append(my_list)
            my_list = []
        else:
            my_list.append(line)
    return(packedls)
##pick up the needed blocks
def pickupblocks(packedlist, tar):
    '''
    This function has to be called after packddy function with an arguement of ddy block list, and this function is to pick up the blocks by a special string in the block
    :param packedlist: This is the packed ddy list with different blocks
    :param tar: This is a special string to recognize the target block
    :return: This function returns a dictionary of the picked block in which the key is the statement in ddy file after "!-"
    '''
    d = {}          ##store data in a dictionary
    for blocks in packedlist:
        for lines in blocks:
            if tar in lines:
                for l in blocks:
                        y = l.replace(" ", "")
                        x = y.split("!-")
                        if len(x) > 1:
                            ##organize data and make the dictionary
                            regex1 = re.compile(r'{.*}\n')
                            regex2 = re.compile(r'\.*\n')
                            str1 = re.sub(regex1, '', x[1])
                            str2 = re.sub(regex2, '', str1)
                            str3 = re.sub("\d+","??", str2)
                            value = re.sub('[^A-Za-z0-9-._\s]+','',x[0])
                            ind = str3
                            d[ind] = value
    return(d)
def parseblock(packedlist: list, tar: object) -> object:
    block = []
    for blocks in packedlist:
        for lines in blocks:
            if tar in lines:
                block.append(blocks)
                block.append("\n")
    return block
def updatesite(packedlist, idf):
    '''
    This function updates the site:Location information in idf file with that in ddy file, this function has to be called after packddy function with an argument of packed ddy list
    :param packedlist: This is the packed ddy list with different blocks
    :param idf: The initial input idf file
    :return: This function returns the site:location part updated idf file
    '''
    idfsite = idf.idfobjects['SITE:LOCATION'][0]
    target = 'Site:Location'
    SiteInformation = pickupblocks(packedlist, target)
    idfsite.Name = SiteInformation.get('LocationName')
    idfsite.Latitude = SiteInformation.get('Latitude')
    idfsite.Longitude = SiteInformation.get('Longitude')
    idfsite.Time_Zone = SiteInformation.get('TimeZoneRelativetoGMT')
    idfsite.Elevation = SiteInformation.get('Elevation')
    return idfsite
##DDY
def updateddyitem(DP0, sizingperiod):
    '''
    This is the process function called by UpdateLocationInfinIDF function which updates each block of design day information
    :param DP0: This is the design period block picked from ddy file
    :param sizingperiod: This is the corresponding block in idf file
    :return: This function returns the updated block in IDF
    '''
    sizingperiod.Name = DP0.get('Name')
    sizingperiod.Month = DP0.get('Month')
    sizingperiod.Day_of_Month = DP0.get('DayofMonth')
    sizingperiod.Day_Type = DP0.get('DayType')
    sizingperiod.Maximum_DryBulb_Temperature = DP0.get('MaximumDry-BulbTemperature')
    sizingperiod.Daily_DryBulb_Temperature_Range = DP0.get('DailyDry-BulbTemperatureRange')
    sizingperiod.DryBulb_Temperature_Range_Modifier_Type = DP0.get('Dry-BulbTemperatureRangeModifierType')
    sizingperiod.DryBulb_Temperature_Range_Modifier_Day_Schedule_Name= DP0.get('Dry-BulbTemperatureRangeModifierScheduleName')
    sizingperiod.Humidity_Condition_Type= DP0.get('HumidityConditionType')
    if DP0.get('HumidityConditionType') == 'Wetbulb'or 'Enthalpy':
        if DP0.get('WetbulbatMaximumDry-Bulb') is None:
            sizingperiod.Wetbulb_or_DewPoint_at_Maximum_DryBulb = ''
        else:
            sizingperiod.Wetbulb_or_DewPoint_at_Maximum_DryBulb= DP0.get('WetbulbatMaximumDry-Bulb')
    if DP0.get('HumidityConditionType') == 'Dewpoint':
        sizingperiod.Wetbulb_or_DewPoint_at_Maximum_DryBulb = DP0.get('DewpointatMaximumDry-Bulb')
    sizingperiod.Humidity_Condition_Day_Schedule_Name=DP0.get('HumidityIndicatingDayScheduleName')
    sizingperiod.Humidity_Ratio_at_Maximum_DryBulb = DP0.get('HumidityRatioatMaximumDry-Bulb')
    sizingperiod.Enthalpy_at_Maximum_DryBulb = DP0.get('EnthalpyatMaximumDry-Bulb')
    sizingperiod.Daily_WetBulb_Temperature_Range = DP0.get('DailyWet-BulbTemperatureRange')
    sizingperiod.Barometric_Pressure = DP0.get('BarometricPressure')
    sizingperiod.Wind_Speed = DP0.get('WindSpeed{m/s}designconditionsvs.traditional??.??m/s(??mph)')
    sizingperiod.Wind_Direction = DP0.get('WindDirection')
    sizingperiod.Rain_Indicator = DP0.get('Rain')
    sizingperiod.Snow_Indicator = DP0.get('Snowonground')
    sizingperiod.Daylight_Saving_Time_Indicator = DP0.get('DaylightSavingsTimeIndicator')
    sizingperiod.Solar_Model_Indicator = DP0.get('SolarModelIndicator')
    sizingperiod.Beam_Solar_Day_Schedule_Name= DP0.get('BeamSolarDayScheduleName')
    sizingperiod.Diffuse_Solar_Day_Schedule_Name = DP0.get('DiffuseSolarDayScheduleName')
    sizingperiod.ASHRAE_Clear_Sky_Optical_Depth_for_Beam_Irradiance_taub = DP0.get('ASHRAEClearSkyOpticalDepthforBeamIrradiance(taub)')
    sizingperiod.ASHRAE_Clear_Sky_Optical_Depth_for_Diffuse_Irradiance_taud = DP0.get('ASHRAEClearSkyOpticalDepthforDiffuseIrradiance(taud)')
    return sizingperiod
def UpdateLocationInfinIDF(idf1,ddyname):
    '''
    This function Automatically updates the location information as well as the design period information in an idf file
    :param idf1: the input idf file which needs to update the design day data and site information
    :param ddyname: This is the path to the directory in which the ddy files are located (relative to the working dir)
    :return: This function returns the updated idf file
    '''
    DDYlist = ['Annual Cooling (DB=>MWB) .4%','Annual Cooling (DP=>MDB) .4%', 'Annual Cooling (Enthalpy=>MDB) .4%','Annual Cooling (WB=>MDB) .4%', 'Annual Heating 99.6%','Annual Heating Wind 99.6% Design Conditions WS=>MCDB','Annual Humidification 99.6% Design Conditions DP=>MCDB']
    for i in range(0, 7):
        sizingprd = idf1.idfobjects['SIZINGPERIOD:DESIGNDAY'][i]
        target = DDYlist[i]
        packedls = packddy(ddyname)
        DP = pickupblocks(packedls, target)
        ##print(DP)
        updateddyitem(DP, sizingprd)
        updatesite(packedls,idf1)
    return idf1
##write epw name into a .csv file for later use of weather file
def WriteEPWNameToCSV(WeatherPath, CsvPath, i):
    '''
    This function automatically writes the csv file with weather file names by reading the name list in the directory where these files stored.
    :param WeatherPath: This is the path to the directory where the weather files are stored
    :param CsvPath: This is the path to the .csv file
    :param i: This is the number of weather files written into the csv file in the loop
    :return: This function returns nothing
    '''
    ls = os.listdir(WeatherPath)
    print (ls)
    with open(CsvPath,'wt') as f:
        k = 0
        for epwitem in ls:
            if k < i:
                 f.writelines(os.path.splitext(epwitem)[0]+"\n")
                 k += 1
## read epw file names
def ReadFileNameInCsv(dir):
    '''
    This function reads the file names stored in a .csv file
    :param dir: This is the path to the directory in which the csv files are located (relative to the working directory)
    :return: A list object in which each element is a file name as a string
    '''
    with open(dir, 'rt') as f:
        filename_list = []
        for i in csv.reader(f):
            for j in i:
                filename_list.append(j)
                if j is None: break
            if i is None: break
        return filename_list
def ReadHVACdesignLoads(resultpath):
    '''

    :return:
    '''
    filehandle = open(resultpath, 'r').read()
    tables = readhtml.lines_table(filehandle)
    line2 = 'Estimated Cooling Peak Load Components'
    line3 = 'Estimated Heating Peak Load Components'
    d = {}
    i=1
    for table2 in tables:
            if line2 in table2[0]:
                targettable = table2[-1]
                d['Zonename' + str(i)] = str(table2[0][2]).split(": ")[1]
                d['LoadClg_'+d['Zonename'+str(i)]] = targettable[26][5]
                d['LoadClg'+d['Zonename'+str(i)]+'_Latent'] = targettable[26][4]
                d['LoadClg' + d['Zonename' + str(i)] + '_Sensible'] = targettable[26][1]+targettable[26][2]
            elif line3 in table2[0]:
                targettable2 = table2[-1]
                d['LoadHtg_'+d['Zonename'+str(i)]] = targettable2[26][5]
                d['LoadHtg'+d['Zonename'+str(i)]+'_Latent'] = targettable2[26][4]
                d['LoadHtg' + d['Zonename' + str(i)] + '_Sensible'] = targettable2[26][1]+targettable2[26][2]
                i+=1
    return d
def compare_two_IDF(file1, file2, resultdir):
    blockHVACfile = packddy(file1)
    blockidealfile = packddy(file2)
    tag = 1
    '''for blocks in blockHVACfile:
        if len(blocks) != 0 and len(blocks) != 1:
            for line in blocks:
                if line.startswith('!-') != True:
                    newHVACblock.append(blocks)
                    break'''
        ##match blocks and pick up the unique HVAC part( skip the name difference )
    for blocks in blockHVACfile:
        for i in range(0, len(blocks)):
            if 'Name' not in blocks[i]:
                b = pickupblocks(blockidealfile, blocks[i])
                if len(b) != 0:
                    tag = 1
                else:
                    tag = 0
                    print(blocks[i])
                    break
            else:
                tag = tag
        if tag == 0:
            with open(resultdir, 'a') as f:
                for lines in blocks:
                    f.write(lines)
                f.write('\n')
def pickupHVACsystem(idfHVACfile, idfObject,zoneloadlist, NodeNumb):
    idfHVAC = IDF(idfHVACfile)
    loopLen = len(idfObject.idfobjects['SIZING:ZONE'])
    for j in range(1, loopLen):
        idfHVAC.copyidfobject(idfHVAC.idfobjects["SIZING:SYSTEM"][0])
        addedobject=idfHVAC.idfobjects["SIZING:SYSTEM"][j]
        addedobject.AirLoop_Name = 'Air Loop HVAC '+str(j+1)
        idfHVAC.copyidfobject(idfHVAC.idfobjects["AIRTERMINAL:SINGLEDUCT:UNCONTROLLED"][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects["ZONEHVAC:EQUIPMENTLIST"][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects["ZONEHVAC:EQUIPMENTCONNECTIONS"][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['FAN:ONOFF'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['COIL:COOLING:DX:SINGLESPEED'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['COIL:HEATING:ELECTRIC'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['COIL:HEATING:DX:SINGLESPEED'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC:UNITARYSYSTEM'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['CONTROLLER:OUTDOORAIR'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['CONTROLLER:MECHANICALVENTILATION'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC:CONTROLLERLIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AVAILABILITYMANAGER:SCHEDULED'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AVAILABILITYMANAGER:SCHEDULED'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AVAILABILITYMANAGERASSIGNMENTLIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AVAILABILITYMANAGERASSIGNMENTLIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['OUTDOORAIR:NODELIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['NODELIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['NODELIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['NODELIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['OUTDOORAIR:MIXER'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC:OUTDOORAIRSYSTEM'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC:ZONESPLITTER'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC:SUPPLYPATH'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AIRLOOPHVAC:ZONEMIXER'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['AirLoopHVAC:ReturnPath'.upper()][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['BRANCH'][0])
        idfHVAC.copyidfobject(idfHVAC.idfobjects['BRANCHLIST'][0])

    ##idfHVAC.printidf()
    for i in range(0, loopLen):
        ZoneName = idfObject.idfobjects['SIZING:ZONE'][i].Zone_or_ZoneList_Name.upper()
        ClgLoad = zoneloadlist['LoadClg_'+ZoneName]
        HtgLoad = zoneloadlist['LoadHtg_'+ZoneName]
        SingleDuct = idfHVAC.idfobjects['AIRTERMINAL:SINGLEDUCT:UNCONTROLLED'][i]
        SingleDuct.Name = 'Diffuser ' + str(i + 1)
        SingleDuct.Zone_Supply_Air_Node_Name = 'Node ' + str(loopLen + 5 + i * 5 + NodeNumb)
        EquipmentLs = idfHVAC.idfobjects['ZONEHVAC:EQUIPMENTLIST'][i]
        EquipmentLs.Name = ZoneName + ' Equipment List'
        EquipmentLs.Zone_Equipment_1_Name = SingleDuct.Name
        EquipmentConnect = idfHVAC.idfobjects['ZONEHVAC:EQUIPMENTCONNECTIONS'][i]
        EquipmentConnect.Zone_Name = ZoneName
        EquipmentConnect.Zone_Conditioning_Equipment_List_Name = ZoneName + ' Equipment List'
        EquipmentConnect.Zone_Air_Inlet_Node_or_NodeList_Name = ZoneName + ' Inlet Node List'
        EquipmentConnect.Zone_Air_Node_Name = 'Node ' + str(i + 1 + NodeNumb)
        EquipmentConnect.Zone_Return_Air_Node_or_NodeList_Name = 'Node ' + str(6 * loopLen + 4 + 4 * i+NodeNumb)
        FAN = idfHVAC.idfobjects['FAN:ONOFF'][i]
        FAN.Name = 'Fan On Off ' + str(i + 1)
        FAN.Air_Inlet_Node_Name = 'Node ' + str(6 * loopLen + 3 + 4 * i+NodeNumb)
        FAN.Air_Outlet_Node_Name = 'Unitary - DX Heat Pump - Cycling - Elec reheat ' + str(
            i + 1) + ' Fan - Cooling Coil Node'
        CoolingDX = idfHVAC.idfobjects['COIL:COOLING:DX:SINGLESPEED'][i]
        CoolingDX.Name = '1 Spd DX Clg Coil ' + str(i + 1)
        CoolingDX.Air_Inlet_Node_Name = 'Unitary - DX Heat Pump - Cycling - Elec reheat ' + str(
            i + 1) + ' Fan - Cooling Coil Node'
        CoolingDX.Air_Outlet_Node_Name = 'Unitary - DX Heat Pump - Cycling - Elec reheat ' + str(
            i + 1) + ' Cooling Coil - Heating Coil Node'
        HeatingElec = idfHVAC.idfobjects['COIL:HEATING:ELECTRIC'][i]
        HeatingElec.Name = 'Elec Htg Coil ' + str(i + 1)
        HeatingElec.Air_Inlet_Node_Name = 'Unitary - DX Heat Pump - Cycling - Elec reheat ' + str(
            i + 1) + ' Heating Coil - Supplemental Coil Node'
        HeatingElec.Air_Outlet_Node_Name = 'Node ' + str(loopLen + 2 + 5 * i+NodeNumb)
        HeatingDX = idfHVAC.idfobjects['COIL:HEATING:DX:SINGLESPEED'][i]
        HeatingDX.Name = '1 Spd DX Htg Coil ' + str(i + 1)
        HeatingDX.Air_Inlet_Node_Name = 'Unitary - DX Heat Pump - Cycling - Elec reheat ' + str(
            i + 1) + ' Cooling Coil - Heating Coil Node'
        HeatingDX.Air_Outlet_Node_Name = 'Unitary - DX Heat Pump - Cycling - Elec reheat ' + str(
            i + 1) + ' Heating Coil - Supplemental Coil Node'
        UnitarySystem = idfHVAC.idfobjects['AIRLOOPHVAC:UNITARYSYSTEM'][i]
        UnitarySystem.Name = 'Unitary - DX Heat Pump - Cycling - Elec reheat ' + str(i + 1)
        UnitarySystem.Controlling_Zone_or_Thermostat_Location = ZoneName
        UnitarySystem.Air_Inlet_Node_Name = 'Node ' + str(loopLen * 6 + 3 + 4 * i+NodeNumb)
        UnitarySystem.Air_Outlet_Node_Name = 'Node ' + str(loopLen + 2 + 5 * i+NodeNumb)
        UnitarySystem.Supply_Fan_Name = FAN.Name
        UnitarySystem.Heating_Coil_Name = HeatingDX.Name
        UnitarySystem.Cooling_Coil_Name = CoolingDX.Name
        UnitarySystem.Supplemental_Heating_Coil_Name = HeatingElec.Name
        ControllerOA = idfHVAC.idfobjects['CONTROLLER:OUTDOORAIR'][i]
        ControllerOA.Name = 'Outdoor Air Controller ' + str(i + 1)
        ControllerOA.Relief_Air_Outlet_Node_Name = 'Node ' + str(loopLen * 6 + 2 + 4 * i+NodeNumb)
        ControllerOA.Return_Air_Node_Name = 'Node ' + str(loopLen + 1 + 5 * i+NodeNumb)
        ControllerOA.Mixed_Air_Node_Name = 'Node ' + str(loopLen * 6 + 3 + 4 * i+NodeNumb)
        ControllerOA.Actuator_Node_Name = 'Node ' + str(loopLen * 6 + 1 + 4 * i+NodeNumb)
        ControllerOA.Mechanical_Ventilation_Controller_Name = 'Controller Mechanical Ventilation ' + str(i + 1)
        ControllerVent = idfHVAC.idfobjects['CONTROLLER:MECHANICALVENTILATION'][i]
        ControllerVent.Name = 'Controller Mechanical Ventilation ' + str(i + 1)
        ControllerVent.Zone_1_Name = ZoneName
        ControllerVent.Design_Specification_Outdoor_Air_Object_Name_1 = idfObject.idfobjects['SIZING:ZONE'][
            i].Design_Specification_Outdoor_Air_Object_Name
        ControllerVent.Design_Specification_Zone_Air_Distribution_Object_Name_1 = idfObject.idfobjects['SIZING:ZONE'][
            i].Design_Specification_Zone_Air_Distribution_Object_Name
        OAControllerls = idfHVAC.idfobjects['AIRLOOPHVAC:CONTROLLERLIST'][i]
        OAControllerls.Name = 'OA System ' + str(i + 1) + ' Controller List'
        OAControllerls.Controller_1_Name = ControllerOA.Name
        AVAILALHVAC = idfHVAC.idfobjects['AVAILABILITYMANAGER:SCHEDULED'][2 * i]
        AVAILALHVAC.Name = 'Air Loop HVAC ' + str(i + 1) + ' Availability Manager'
        AVAILALHVAC.Schedule_Name = 'Always On Discrete'
        AVAILOA = idfHVAC.idfobjects['AVAILABILITYMANAGER:SCHEDULED'][2 * i + 1]
        AVAILOA.Name = 'OA System ' + str(i + 1) + ' Availability Manager'
        AVAILOA.Schedule_Name = 'Always On Discrete'
        AMAL = idfHVAC.idfobjects['AVAILABILITYMANAGERASSIGNMENTLIST'][2 * i]
        AMAL.Name = 'Air Loop HVAC ' + str(i + 1) + 'Availability Manager List'
        AMAL.Availability_Manager_1_Name = AVAILALHVAC.Name
        AMAL2 = idfHVAC.idfobjects['AVAILABILITYMANAGERASSIGNMENTLIST'][2 * i + 1]
        AMAL2.Name = 'OA System ' + str(i + 1) + ' Availability Manager List'
        AMAL2.Availability_Manager_1_Name = AVAILOA.Name
        OANodeLs = idfHVAC.idfobjects['OUTDOORAIR:NODELIST'][i]
        OANodeLs.Node_or_NodeList_Name_1 = 'Node ' + str(6 * loopLen + 1 + 4 * i+NodeNumb)
        NodeLs_ZoneInlet = idfHVAC.idfobjects['NODELIST'][i]
        NodeLs_ZoneInlet.Name = ZoneName + " Inlet Node List"
        NodeLs_ZoneInlet.Node_1_Name = 'Node ' + str(loopLen + 5 + 5 * i+NodeNumb)
        NodeLs_ALSupplyOut = idfHVAC.idfobjects['NODELIST'][loopLen + 2 * i]
        NodeLs_ALDemandIn = idfHVAC.idfobjects['NODELIST'][loopLen + 2 * i + 1]
        NodeLs_ALSupplyOut.Name = 'Air Loop HVAC ' + str(i + 1) + ' Supply Outlet Nodes'
        NodeLs_ALDemandIn.Name = 'Air Loop HVAC ' + str(i + 1) + ' Demand Inlet Nodes'
        NodeLs_ALSupplyOut.Node_1_Name = 'Node ' + str(loopLen + 2 + 5 * i+NodeNumb)
        NodeLs_ALDemandIn.Node_1_Name = 'Node ' + str(loopLen + 3 + 5 * i+NodeNumb)
        ALHVAC = idfHVAC.idfobjects['AIRLOOPHVAC'][i]
        ALHVAC.Name = 'Air Loop HVAC ' + str(i + 1)
        ALHVAC.Availability_Manager_List_Name = AMAL.Name
        ALHVAC.Branch_List_Name = 'Air Loop HVAC ' + str(i + 1) + ' Supply Branches'
        ALHVAC.Supply_Side_Inlet_Node_Name = 'Node ' + str(loopLen + 1 + 5 * i+NodeNumb)
        ALHVAC.Demand_Side_Outlet_Node_Name = 'Node ' + str(loopLen + 4 + 5 * i+NodeNumb)
        ALHVAC.Demand_Side_Inlet_Node_Names = NodeLs_ALDemandIn.Name
        ALHVAC.Supply_Side_Outlet_Node_Names = NodeLs_ALSupplyOut.Name
        OAMixer = idfHVAC.idfobjects['OUTDOORAIR:MIXER'][i]
        OAMixer.Name = 'OA System ' + str(i + 1) + ' Outdoor Air Mixer'
        OAMixer.Mixed_Air_Node_Name = 'Node ' + str(6 * loopLen + 3 + 4 * i+NodeNumb)
        OAMixer.Outdoor_Air_Stream_Node_Name = 'Node ' + str(6 * loopLen + 1 + 4 * i+NodeNumb)
        OAMixer.Relief_Air_Stream_Node_Name = 'Node ' + str(6 * loopLen + 2 + 4 * i+NodeNumb)
        OAMixer.Return_Air_Stream_Node_Name = 'Node ' + str(loopLen + 1 + 5 * i+NodeNumb)
        ALOASysEquip = idfHVAC.idfobjects['AIRLOOPHVAC:OUTDOORAIRSYSTEM:EQUIPMENTLIST'][i]
        ALOASysEquip.Name = 'OA System ' + str(i + 1) + ' Equipment List'
        ALOASysEquip.Component_1_Name = OAMixer.Name
        OASys = idfHVAC.idfobjects['AIRLOOPHVAC:OUTDOORAIRSYSTEM'][i]
        OASys.Name = 'OA System ' + str(i + 1)
        OASys.Controller_List_Name = OAControllerls.Name
        OASys.Outdoor_Air_Equipment_List_Name = ALOASysEquip.Name
        OASys.Availability_Manager_List_Name = AMAL2.Name
        ZoneSplitter = idfHVAC.idfobjects['AIRLOOPHVAC:ZONESPLITTER'][i]
        ZoneSplitter.Name = 'Air Loop HVAC Zone Splitter ' + str(i + 1)
        ZoneSplitter.Inlet_Node_Name = 'Node ' + str(loopLen + 3 + 5 * i+NodeNumb)
        ZoneSplitter.Outlet_1_Node_Name = 'Node ' + str(loopLen + 5 + 5 * i+NodeNumb)
        SupplyPath = idfHVAC.idfobjects['AIRLOOPHVAC:SUPPLYPATH'][i]
        NodeNumber = str(loopLen + 3 + 5 * i+NodeNumb)
        SupplyPath.Name = 'Air Loop HVAC ' + str(i + 1) + ' Node ' + NodeNumber + ' Supply Path'
        SupplyPath.Supply_Air_Path_Inlet_Node_Name = 'Node ' + NodeNumber
        SupplyPath.Component_1_Name = 'Air Loop HVAC Zone Splitter ' + str(i + 1)
        ZoneMixer = idfHVAC.idfobjects['AIRLOOPHVAC:ZONEMIXER'][i]
        ZoneMixer.Name = 'Air Loop HVAC Zone Mixer ' + str(i + 1)
        ZoneMixer.Outlet_Node_Name = 'Node ' + str(loopLen + 4 + 5 * i+NodeNumb)
        ZoneMixer.Inlet_1_Node_Name = 'Node ' + str(loopLen * 6 + 4 + 4 * i+NodeNumb)
        RetPath = idfHVAC.idfobjects['AirLoopHVAC:ReturnPath'.upper()][i]
        RetPath.Name = 'Air Loop HVAC ' + str(i + 1) + ' Return Path'
        RetPath.Return_Air_Path_Outlet_Node_Name = 'Node ' + str(loopLen + 4 + 5 * i+NodeNumb)
        RetPath.Component_1_Name = ZoneMixer.Name
        Branch = idfHVAC.idfobjects['BRANCH'][i]
        Branch.Name = 'Air Loop HVAC ' + str(i + 1) + ' Main Branch'
        Branch.Component_1_Name = OASys.Name
        Branch.Component_1_Inlet_Node_Name = 'Node ' + str(loopLen + 1 + i * 5+NodeNumb)
        Branch.Component_1_Outlet_Node_Name = 'Node ' + str(loopLen * 6 + 3 + 4 * i+NodeNumb)
        Branch.Component_2_Name = UnitarySystem.Name
        Branch.Component_2_Inlet_Node_Name = Branch.Component_1_Outlet_Node_Name
        Branch.Component_2_Outlet_Node_Name = 'Node ' + str(loopLen + 2 + 5 * i+NodeNumb)
        BranchLs = idfHVAC.idfobjects['BRANCHLIST'][i]
        BranchLs.Name = ALHVAC.Branch_List_Name
        BranchLs.Branch_1_Name = Branch.Name
        if abs(int(HtgLoad)) in range(0, 4689) and abs(int(ClgLoad)) in range(0, 3399):
            FAN.Maximum_Flow_Rate= '0.1665974474496'
            CoolingDX.Gross_Rated_Total_Cooling_Capacity = '3399.62441399778'
            CoolingDX.Gross_Rated_Cooling_COP='3.78'
            HeatingDX.Gross_Rated_Heating_Capacity='4689.13712275556'
            HeatingDX.Gross_Rated_Heating_COP = '3.08'
        elif abs(int(HtgLoad)) in range(0, 7912) and abs(int(ClgLoad)) in range(0, 7033):
            FAN.Maximum_Flow_Rate = '0.3246998409216'
            CoolingDX.Gross_Rated_Total_Cooling_Capacity = '7033.705684133'
            CoolingDX.Gross_Rated_Cooling_COP='3.52'
            HeatingDX.Gross_Rated_Heating_Capacity='7912.91889465'
            HeatingDX.Gross_Rated_Heating_COP = '2.93'
        elif abs(int(HtgLoad)) in range(0,11722) and abs(int(ClgLoad)) in range(0,10550):
            FAN.Maximum_Flow_Rate = '0.533300610816'
            CoolingDX.Gross_Rated_Total_Cooling_Capacity = '10550.5585262'
            CoolingDX.Gross_Rated_Cooling_COP='3.55'
            HeatingDX.Gross_Rated_Heating_Capacity='11722.8428068889'
            HeatingDX.Gross_Rated_Heating_COP = '2.7'
        else:
            print("HVAC Sizes could not meet demand")
            print(abs(HtgLoad), abs(ClgLoad))
    return idfHVAC
def ChangeSurfaceToCorner(idf, CornerSurfaceName):
    Surface = idf.idfobjects['BuildingSurface:Detailed'.upper()]
    for surfaces in Surface:
        if surfaces.Name == CornerSurfaceName:
            surfaces.Construction_Name = 'Wall'
            surfaces.Outside_Boundary_Condition = 'Outdoors'
            surfaces.Sun_Exposure = 'SunExposed'
            surfaces.Wind_Exposure = 'WindExposed'
    return idf
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

##set idd file
rundirname = 'C:\\Users\\yueyue.zhou\\Documents\\Intern\\Hospitality\\'
iddfile = rundirname+ "\\Energy+.idd"
#An idd file is required to run the simulation, usually could be in the EnergyPlus folder
IDF.setiddname(iddfile)

WeatherDir = 'C:\\EnergyPlusV8-9-0\\WeatherData\\weather_files_ddy_epw_stat\\'
#Folder to store weather files
epwDir = WeatherDir + 'epw\\USA\\'
ddyDir = WeatherDir + 'ddy\\USA\\'

CSVDir = 'C:\\Users\\yueyue.zhou\\Documents\\Intern\\Hospitality\\WeatherFileNameList.csv'
#The csv file to define the weather files to pick up for simulation

##WriteEPWNameToCSV(epwDir, CSVDir , 8)
#This could help write a specific number of weather files to .csv file

weatherfilename_list = ReadFileNameInCsv(CSVDir)
print(weatherfilename_list)


# Read all the idf models for simulation and make a list
IdfDirInitial = rundirname + 'idf\\'
LargeIDFDir = IdfDirInitial+'Large\\'
SmallIDFDir = IdfDirInitial + 'Small\\'
LargeIDFLs = os.listdir(LargeIDFDir)
SmallIDFLs = os.listdir(SmallIDFDir)

CoolingLoads = []
HeatingLoads = []
ClgSensible = []
ClgLatent = []
HtgSensible = []
HtgLatent = []
Parameters = []

##run with different locations loop
for i in weatherfilename_list:
    #pick up the epw and ddy files by file name
    epwname = epwDir + i +'.epw'
    ddyname = ddyDir + i +'.ddy'
    GeneratedIDFdir = rundirname + "idfGenerated\\" +i +'\\'
    createFolder(GeneratedIDFdir)
    for j in range(0,len(LargeIDFLs)):
        fname1 = LargeIDFDir + LargeIDFLs[j]
        idf1 = IDF(fname1, epwname)
        UpdateLocationInfinIDF(idf1,ddyname)
        ##combined all ddy functions with this function to update the site, design period information in IDF files

        #Change the Window Constructions
        WinMaterial = idf1.idfobjects['WindowMaterial:SimpleGlazingSystem'.upper()][0]
        WinMaterial.UFactor = '1.81704416'
        WinMaterial.Name = 'TypicalWindow U0.32 SHGC0.25'
        WinMaterial.Solar_Heat_Gain_Coefficient= '0.25'
        WindowConst = idf1.idfobjects['Construction'.upper()][10]
        WindowConst.Outside_Layer = WinMaterial.Name

        #Change the slab construction
        NoMassCarpet = idf1.idfobjects['Material:NoMass'.upper()][0]
        NoMassGravel = idf1.idfobjects['Material:NoMass'.upper()][3]
        NoMassCarpet.Thermal_Resistance = '0.190199009802822'
        NoMassGravel.Thermal_Resistance = '1.40888155409498'

        #Change the wall construction
        NoMassWall = idf1.idfobjects['Material:NoMass'.upper()][2]
        NoMassWall.Thermal_Resistance = '3.34609369097557'

        #Add the zonecomponentloadsummary report output
        SummaryReport = idf1.idfobjects['Output:Table:SummaryReports'.upper()]
        SummaryReport[0].Report_2_Name = 'ZoneComponentLoadSummary'

        #Create folder for each model
        TypeDir = GeneratedIDFdir + LargeIDFLs[j].split('.')[0] +'\\'
        createFolder(TypeDir)

        building = idf1.idfobjects['BUILDING'][0]
        #Loop for different orientations
        for axis in [0,90,180,270]:
            building.North_Axis = axis
            LocationIDF = TypeDir + 'Orientation_'+ str(axis) + '.idf'
            idf1.saveas(LocationIDF)

            #Define the folder path to store the results
            resultsdir = rundirname + 'Results\\' + i + '\\' + LargeIDFLs[j].split('.')[0]+'\\'+str(axis)
            createFolder(resultsdir)
            idf1.run(output_directory=resultsdir, expandobjects = True)

            #Parse the peak load results
            d = ReadHVACdesignLoads(resultsdir+'\\eplustbl.htm')
            print(d)

            #Store the peak load data to the lists
            for v in range(15):
                CoolingLoads.append(d.get('LoadClg_'+d.get('Zonename1')) )
                ClgSensible.append(d.get('LoadClg'+d.get('Zonename1')+'_Sensible'))
                ClgLatent.append(d.get('LoadClg' + d.get('Zonename1') + '_Latent'))
                HeatingLoads.append(d.get('LoadHtg_'+d.get('Zonename1')) )
                HtgSensible.append(d.get('LoadHtg'+d.get('Zonename1')+'_Sensible'))
                HtgLatent.append(d.get('LoadHtg' + d.get('Zonename1') + '_Latent'))
                Parameters.append(i + "_" +str(axis) + '_'+LargeIDFLs[j].split('.')[0]+ '_' + 'MiddleUnit')

            #find the surface to change from adiabatic to exterior wall and call this function to implement the change
            idf2 = ChangeSurfaceToCorner(idf1, 'Surface 5')
            CornerIDF = TypeDir + 'Corner_'+ str(axis) + '.idf'
            idf2.saveas(CornerIDF)

            # Define the folder path to store the results for corner units
            resultsdir2 = rundirname + 'Results\\' + i +'\\'+LargeIDFLs[j].split('.')[0]+'_Corner' + '\\'+str(axis)
            createFolder(resultsdir2)
            idf2.run(output_directory=resultsdir2, expandobjects=True)

            # Parse the peak load results
            d = ReadHVACdesignLoads(resultsdir2+'\\eplustbl.htm')
            print(d)
            # Store the peak load data to the lists
            for v in range(4):
                CoolingLoads.append(d.get('LoadClg_'+d.get('Zonename1')) )
                ClgSensible.append(d.get('LoadClg'+d.get('Zonename1')+'_Sensible'))
                ClgLatent.append(d.get('LoadClg' + d.get('Zonename1') + '_Latent'))
                HeatingLoads.append(d.get('LoadHtg_'+d.get('Zonename1')) )
                HtgSensible.append(d.get('LoadHtg'+d.get('Zonename1')+'_Sensible'))
                HtgLatent.append(d.get('LoadHtg' + d.get('Zonename1') + '_Latent'))
                Parameters.append(i + "_" + str(axis) + '_' + LargeIDFLs[j].split('.')[0] + '_' + 'CornerUnit')


    ##For small units, the process is similar to the large units
    for k in range(0,len(SmallIDFLs)):
        fname_1 = SmallIDFDir + SmallIDFLs[k]
        idf_1 = IDF(fname_1, epwname)
        UpdateLocationInfinIDF(idf_1,ddyname)    ##combined all ddy functions with this function to update the site, design period information in IDF files
        WinMaterial = idf_1.idfobjects['WindowMaterial:SimpleGlazingSystem'.upper()][0]
        WinMaterial.UFactor = '1.81704416'
        WinMaterial.Name = 'TypicalWindow U0.32 SHGC0.25'
        WinMaterial.Solar_Heat_Gain_Coefficient= '0.25'
        WindowConst = idf_1.idfobjects['Construction'.upper()][10]
        WindowConst.Outside_Layer = WinMaterial.Name
        NoMassCarpet = idf_1.idfobjects['Material:NoMass'.upper()][0]
        NoMassWall = idf_1.idfobjects['Material:NoMass'.upper()][2]
        NoMassGravel = idf_1.idfobjects['Material:NoMass'.upper()][3]
        NoMassCarpet.Thermal_Resistance = '0.190199009802822'
        NoMassWall.Thermal_Resistance = '3.34609369097557'
        NoMassGravel.Thermal_Resistance = '1.40888155409498'
        TypeDir = GeneratedIDFdir + SmallIDFLs[k].split('.')[0] + '\\'
        createFolder(TypeDir)
        SummaryReport = idf_1.idfobjects['Output:Table:SummaryReports'.upper()]
        SummaryReport[0].Report_2_Name = 'ZoneComponentLoadSummary'
        building = idf_1.idfobjects['BUILDING'][0]
        for Axis in [0,90,180,270]:
            building.North_Axis = Axis
            LocationIDF = TypeDir + 'Orientation_'+ str(Axis) + '.idf'
            idf_1.saveas(LocationIDF)
            results_dir = rundirname + 'Results\\' + i + '\\' + SmallIDFLs[k].split('.')[0]+'\\'+str(Axis)
            createFolder(results_dir)
            idf_1.run(output_directory=results_dir, expandobjects = True)

            d = ReadHVACdesignLoads(results_dir+'\\eplustbl.htm')
            print(d)
            for v in range(15):
                CoolingLoads.append(d.get('LoadClg_'+d.get('Zonename1')) )
                ClgSensible.append(d.get('LoadClg'+d.get('Zonename1')+'_Sensible'))
                ClgLatent.append(d.get('LoadClg' + d.get('Zonename1') + '_Latent'))
                HeatingLoads.append(d.get('LoadHtg_'+d.get('Zonename1')) )
                HtgSensible.append(d.get('LoadHtg'+d.get('Zonename1')+'_Sensible'))
                HtgLatent.append(d.get('LoadHtg' + d.get('Zonename1') + '_Latent'))
                Parameters.append(
                    i + "_" + str(Axis) + '_' + SmallIDFLs[k].split('.')[0] + '_' + 'MiddleUnit')

            idf_2 = ChangeSurfaceToCorner(idf_1, 'Surface 4')
            Corner_IDF = TypeDir + 'Corner_'+ str(Axis) + '.idf'
            idf_2.saveas(Corner_IDF)
            results_dir2 = rundirname + 'Results\\' + i +'\\'+SmallIDFLs[k].split('.')[0]+'_Corner' + '\\'+str(Axis)
            createFolder(results_dir2)
            idf_2.run(output_directory=results_dir2, expandobjects=True)

            d = ReadHVACdesignLoads(results_dir2+'\\eplustbl.htm')
            print(d)
            for v in range(4):
                CoolingLoads.append(d.get('LoadClg_'+d.get('Zonename1')) )
                ClgSensible.append(d.get('LoadClg'+d.get('Zonename1')+'_Sensible'))
                ClgLatent.append(d.get('LoadClg' + d.get('Zonename1') + '_Latent'))
                HeatingLoads.append(d.get('LoadHtg_'+d.get('Zonename1')) )
                HtgSensible.append(d.get('LoadHtg'+d.get('Zonename1')+'_Sensible'))
                HtgLatent.append(d.get('LoadHtg' + d.get('Zonename1') + '_Latent'))
                Parameters.append(
                    i + "_" + str(Axis) + '_' + SmallIDFLs[k].split('.')[0] + '_' + 'CornerUnit')

#Store the results to pandas data structure and write the results to csv
CS = pd.Series(CoolingLoads)
CSS = pd.Series(ClgSensible)
CLS = pd.Series(ClgLatent)
HS = pd.Series(HeatingLoads)
HSS = pd.Series(HtgSensible)
HLS = pd.Series(HtgLatent)
ParS= pd.Series(Parameters)
df = pd.DataFrame().assign(CoolingLoads=CS.values, CoolingSensibleLoads=CSS.values, CoolingLatentLoads=CLS.values,
                           HeatingLoads=HS.values, HeatingSensibleLoads=HSS.values,HeatingLatentLoads=HLS.values,
                           parameters = ParS.values )
print (df)
df.to_csv(path_or_buf=rundirname + 'PeakLoads_PARAMETERS.csv')

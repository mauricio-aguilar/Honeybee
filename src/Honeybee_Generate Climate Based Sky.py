#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2016, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Genrate Climate Based Sky

This component generate a climate based sky for any hour of the year
-
Provided by Honeybee 0.0.59
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _weatherFile: epw weather file address on your system
        _month: Month of the study [1-12]
        _day: Day of the study [1-31]
        _hour: Hour of the study [1-24]
    Returns:
        radiationValues: Direct and diffuse radiation of the sky
        skyFilePath: Sky file location on the local drive
"""

ghenv.Component.Name = "Honeybee_Generate Climate Based Sky"
ghenv.Component.NickName = 'genClimateBasedSky'
ghenv.Component.Message = 'VER 0.0.59\nJAN_26_2016'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "02 | Daylight | Sky"
#compatibleHBVersion = VER 0.0.56\nFEB_01_2015
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import os
import scriptcontext as sc
import Grasshopper.Kernel as gh
import math

def date2Hour(month, day, hour):
    # fix the end day
    numOfDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    # dd = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    JD = numOfDays[int(month)-1] + int(day)
    return (JD - 1) * 24 + hour

def getRadiationValues(epw_file, HOY):
    epwfile = open(epw_file,"r")
    for lineCount, line in enumerate(epwfile):
        if lineCount == int(HOY + 8 - 1):
            dirRad = (float(line.split(',')[14]))
            difRad = (float(line.split(',')[15]))
    return dirRad, difRad

def RADDaylightingSky(epwFileAddress, locName, lat, long, timeZone, hour, day, month,  north = 0):
    
    dirNrmRad, difHorRad = getRadiationValues(epwFileAddress, date2Hour(month, day, hour))
    
    print "Direct: " + `dirNrmRad` + "| Diffuse: " + `difHorRad`
    
    return  "# start of sky definition for daylighting studies\n" + \
            "# location name: " + locName + " LAT: " + lat + "\n" + \
            "!gendaylit " + `month` + ' ' + `day` + ' ' + `hour` + \
            " -a " + lat + " -o " + `-float(long)` + " -m " + `-float(timeZone) * 15` + \
            " -W " + `dirNrmRad` + " " + `difHorRad` + " -O " + `outputType` + \
            " | xform -rz " + str(north) + "\n" + \
            "skyfunc glow sky_mat\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "1 1 1 0\n" + \
            "sky_mat source sky\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "0 0 1 180\n" + \
            "skyfunc glow ground_glow\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "1 .8 .5 0\n" + \
            "ground_glow source ground\n" + \
            "0\n" + \
            "0\n" + \
            "4\n" + \
            "0 0 -1 180\n"


def main(outputType, weatherFile, month, day, hour, north = 0):

    # import the classes
    if sc.sticky.has_key('honeybee_release') and sc.sticky.has_key('ladybug_release'):

        try:
            if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
            if sc.sticky['honeybee_release'].isInputMissing(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Honeybee to use this compoent." + \
            "Use updateHoneybee component to update userObjects.\n" + \
            "If you have already updated userObjects drag Honeybee_Honeybee component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        hb_folders = sc.sticky["honeybee_folders"]
        hb_RADPath = hb_folders["RADPath"]
        hb_RADLibPath = hb_folders["RADLibPath"]
        
    else:
        print "You should first let Honeybee to fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug and Honeybee to fly...")
        return -1
    
    # check forgendaylit exist
    if not os.path.isfile(hb_RADPath + "\\gendaylit.exe"):
        msg = "Cannot find gendaylit.exe at " + hb_RADPath + \
              "Make sure that gendaylit is installed on your system."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return -1
    
    if weatherFile != None and weatherFile[-3:] == 'epw':
        if not os.path.isfile(weatherFile):
            print "Can't find the weather file at: " + weatherFile
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Can't find the weather file at: " + weatherFile)
            return -1
        
        # import data from epw file data
        locName, lat, lngt, timeZone, elev, locationStr = lb_preparation.epwLocation(weatherFile)
        newLocName = lb_preparation.removeBlank(locName)
    else:
        print "epwWeatherFile address is not a valid .epw file"
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "epwWeatherFile address is not a valid .epw file")
        return -1
        
    # make new folder for each city
    subWorkingDir = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "skylib\\climateBasedSkies\\", newLocName)
    subWorkingDir = lb_preparation.makeWorkingDir(subWorkingDir)
    # print 'Current working directory is set to: ', subWorkingDir
    
    outputFile = subWorkingDir + "\\climateBasedSky@_" + `month` + "_" + `day` + "@" + ('%.2f'%hour).replace(".", "") + ".sky"

    northAngle, northVector = lb_preparation.angle2north(north)

    skyStr = RADDaylightingSky(weatherFile, newLocName, lat, lngt, timeZone, hour, day, month, math.degrees(northAngle))
    
    skyFile = open(outputFile, 'w')
    skyFile.write(skyStr)
    skyFile.close()
    
    return outputFile , `day` + "_" + `month` + "@" + ('%.2f'%hour).replace(".", "")
    
if _weatherFile!=None and _month!=None and _day!=None and _hour!=None:
    outputType = 0
    result = main(outputType, _weatherFile, _month, _day, _hour, north_)
    if result!=-1:
        skyFilePath, skyDescription = result

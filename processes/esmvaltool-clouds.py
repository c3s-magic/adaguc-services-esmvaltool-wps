"""
../wps.py?request=execute
&service=wps
&version=1.0.0
&identifier=esmvaltool-perfmetrics
&status=true
&storeExecuteResponse=true


"""
import datetime

import shutil

import netCDF4
import urlparse

from pywps.Process import WPSProcess
import os
import logging
from jinja2 import FileSystemLoader, Environment,select_autoescape
import glob


class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(self,
                            identifier="esmvaltool-clouds",  # the same as the file name
                            version="1.0",
                            title="Clouds Diagnostics",
                            storeSupported="True",
                            statusSupported="True",
                            abstract="Create Cloud diagnostics using ESMValTool (takes about 2 minutes).",
                            grassLocation=False)

        self.startYear = self.addLiteralInput(identifier="startYear",
                                              title="First year data used in plot",
                                              type="Integer",
                                              default=2003,
                                              minOccurs=1,
                                              maxOccurs=1)

        self.endYear = self.addLiteralInput(identifier="endYear",
                                            title="Last year data used in plot",
                                            type="Integer",
                                            default=2005,
                                            minOccurs=1,
                                            maxOccurs=1)

#        self.opendapURL = self.addLiteralOutput(identifier="opendapURL",
#                                                title="opendapURL",
#                                                type="String", )


	self.plots = []
	for i in range (0,8):
		self.plots.append(self.addComplexOutput(identifier = "plot%d" % i,
		     title = "Plot",
		     formats = [
			 {"mimeType":"image/png"}
		     ]))


    def execute(self):
        self.status.set("starting", 0)

        #print some debugging info

	start_year = self.startYear.getValue()
        end_year = self.endYear.getValue()

	# This does not work atm.
        # This allows the NetCDF library to find the users credentials (X509 cert)
        # Set current working directory to user HOME dir
        os.chdir(os.environ['HOME'])

        # Create output folder name
        output_folder_name = "WPS_" + self.identifier + "_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        logging.debug(os.environ['POF_OUTPUT_PATH'])

        #OpenDAP Url prefix (hosted by portal)
        output_folder_url = os.environ['POF_OUTPUT_URL'] + output_folder_name

        #Filesystem output path
        output_folder_path = os.path.join(os.environ['POF_OUTPUT_PATH'], output_folder_name)

        logging.debug("output folder path is %s" % output_folder_path)

        #Create output directory
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        #copy input files to scratch (in correct folders for esmvaltool)

        #next, copy input netcdf to a location esmvaltool expects

        # example cmpi5 esgf link
        # http://esgf-data1.ceda.ac.uk/thredds/dodsC/esg_dataroot/cmip5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/v1/tas/tas_Amon_ACCESS1-0_historical_r1i1p1_185001-200512.nc

        # esmvaltool data folder example
        # ETHZ_CMIP5/historical/Amon/ta/bcc-csm1-1/r1i1p1/ta_Amon_bcc-csm1-1_historical_r1i1p1_200001-200212.nc


        	#description = <model> SOME DESCRIPTION FIELDS HERE </model>

        self.status.set("setting up namelist for esmvaltool", 10)

        #create esmvaltool config (using template)
        environment = Environment(loader=FileSystemLoader('/namelists'))
                                  #autoescape=select_autoescape(['html', 'xml']))

        template = environment.get_template('namelist_clouds.xml')

        generated_namelist = template.render(work_dir=output_folder_path)

        logging.debug("template output = %s" % generated_namelist)

        #write generated namelist to file

        namelist_path = output_folder_path + "/" + 'namelist.xml'

        namelist_fd = open(namelist_path, 'w')
        namelist_fd.write(generated_namelist)
        namelist_fd.close()

        #run esmvaltool command

        self.status.set("running esmvaltool", 20)

        os.chdir('/src/ESMValTool')

        self.cmd(['python', 'main.py', namelist_path])

        #grep output from output folder

        self.status.set("processing output", 90)

        output_images = sorted(glob.glob(output_folder_path + "/clouds*/*.png"))

	for i in range(0, len(output_images)):

		image = output_images[i]

                logging.debug("output image path is %s" % image)

#        rel_output_image = os.path.relpath(output_image, output_folder_path)
#        plot_url = output_folder_url + "/" + rel_output_image

                self.plots[i].setValue(image)

                #KNMI WPS Specific Set output

        self.status.set("ready", 100);

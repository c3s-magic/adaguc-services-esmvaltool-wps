"""

Example processing returning some image

"""
import logging
import os
import shutil

from pywps.Process.Process import WPSProcess

class Process(WPSProcess):
     def __init__(self):
         # init process
         WPSProcess.__init__(self,
                             identifier="pretty-picture", #the same as the file name
                             version = "1.0",
                             title="Some picture",
                             storeSupported = "true",
                             statusSupported = "true",
                             abstract="Some picture.",
                             grassLocation =False)

         #Input (c4i fails if no inputs are present)
	 self.tag = self.addLiteralInput(identifier="tag",title = "Specify a custom title for this process",type="String",default="unspecified")

	 self.picture=self.addComplexOutput(identifier="picture",
                    title="Raster out",
                    formats=[{"mimeType":"image/png"}])

	 self.picture2=self.addComplexOutput(identifier="picture2",
                    title="Raster out",
                    formats=[{"mimeType":"image/png"}])

     def execute(self):
         outfile = "/miniconda/lib/python2.7/site-packages/matplotlib/backends/web_backend/jquery/css/themes/base/images/ui-icons_228ef1_256x240.png"
#	 self.picture.format = {'mimeType':"image/png"}
         self.picture.setValue(outfile)
         self.picture2.setValue(outfile)

#	 dir(self)
#	 self.processTitle.setValue(self.tag.getValue())


#	 logging.debug('output path is', os.environ['POF_OUTPUT_PATH'])
#	 logging.debug('output url is', os.environ['POF_OUTPUT_URL'])

#	 shutil.copy(outfile, os.environ['POF_OUTPUT_PATH'])

#	 filelink = 'https://upload.wikimedia.org/wikipedia/commons/d/df/LocationOceans.png'
#	 filelink = os.environ['POF_OUTPUT_URL'] + '/' + 'ui-icons_228ef1_256x240.png'
#         self.morepicture.setValue(filelink)

         return


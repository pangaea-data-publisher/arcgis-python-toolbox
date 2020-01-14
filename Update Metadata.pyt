import arcpy
import sys #running in python2 version may cause problem like "ascii codec can't encode character"
reload(sys)
sys.setdefaultencoding('utf8') #By importing & reloading the sys module and set the value will clear the error

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Update Metadata"
        self.alias = "update_metadata"
	
        # List of tool classes associated with this toolbox
        self.tools = [UpdateMetadata]


class UpdateMetadata(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update Metadata"
        self.description = "This toolbox get the metadata from the pangaea dataset using pangaeapy module either by using a integer ID or an DOI of the dataset " + \
	"and updates the Geodatabase with a metadata."
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""

	# First Parameter i.e., Input geodatabase with tracklines
	input_dataset = arcpy.Parameter(
		displayName="Input Vector Dataset",
		name="input_dataset",
		datatype=["DEGeodatasetType"],
		parameterType="Required",
		direction="Input")
		

	# Output parameter which clones the input dataset and updates the attribute table with values
	output_dataset = arcpy.Parameter(
		displayName="Output Vector Dataset",
		name="output_dataset",
		datatype=["DEGeodatasetType"],
		parameterType="Derived",
		direction="Output")

	output_dataset.parameterDependencies = [input_dataset.name]
	#output_dataset.schema.clone = True

	params = [input_dataset, output_dataset]
	return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
	inputdataset = parameters[0].valueAsText #getting the parameters
	
	#Define the field length if it is more than 255 characters
	arcpy.AddField_management(inputdataset, "Citation", "TEXT" ,field_length = 1000)
	arcpy.AddField_management(inputdataset, "Projects", "TEXT" ,field_length = 1000 )
	arcpy.AddField_management(inputdataset, "Events", "TEXT" ,field_length = 5000 )
	
	expression = '''
from pangaeapy import PanDataSet

def getCitation(p_dataset_id):
	ds=PanDataSet(p_dataset_id)
	return ds.citation
	
def getprojects(p_dataset_id):
	ds=PanDataSet(p_dataset_id)
	projects=""
	
	def listOfTuples(l1,l2,l3):
		return list(map(lambda x,y,z:(x,y,z),l1,l2,l3))
	
	"""The toolbox is designed to the store the values in list form in python and it is converted to string format
  	to display in the attribute table of geodatabase. Because the list format to store values in geodatabase is not supported."""
	# Tuple can't be displayed in the attribute table consecutively. So the values are converted to list.
	proj_label=[]
	proj_name=[]
	proj_URL=[]
	
	for proj in ds.projects:
		#Both label and name are hypertext. To get the text of the element text.strip() is used.
		proj_label.append(proj.label.text.strip())
		proj_name.append(proj.name.text.strip())
		proj_URL.append(proj.URL.text.strip())
		#merge_projects= [(proj_label[i],proj_name[i],proj_URL[i]) for i in range(0,len(proj_label))]
		merge_projects=listOfTuples(proj_label,proj_name,proj_URL)
		
		#converting a python list to a string for display in attribute table
		projects='/n'.join(map(str,merge_projects))
		
	return projects
	
def getevents(p_dataset_id):
	ds=PanDataSet(p_dataset_id)
	events=""
	
	def listOfTuples(l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11):
		return list(map(lambda a,b,c,d,e,f,g,h,i,j,k:(a,b,c,d,e,f,g,h,i,j,k),l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11))
	
	event_label=[]
	start_latitude=[]
	start_longitude=[]
	end_latitude=[]
	end_longitude=[]
	start_datetime=[]
	end_datetime=[]
	location=[]
	campaign=[]
	basis=[]
	device=[]
	
	for eve in ds.events:
		event_label.append(eve.label)
		start_latitude.append("Latitude Start:{}".format(eve.latitude))
		start_longitude.append("Longitude Start:{}".format(eve.longitude))
		end_latitude.append("Latitude End:{}".format(eve.latitude2))
		end_longitude.append("Longitude End:{}".format(eve.longitude2))
		start_datetime.append("Date/Time Start:{}".format(eve.datetime))
		end_datetime.append("Date/Time End:{}".format(eve.datetime2))
		location.append("Location:{}".format(eve.location))
		campaign.append("Campaign:{}".format(eve.campaign))
		basis.append("Basis:{}".format(eve.basis))
		device.append("Device:{}".format(eve.device))
		merge_events=listOfTuples(event_label,start_latitude,start_longitude,end_latitude,end_longitude,start_datetime,end_datetime,location,campaign,basis,device)
		
		#final_merged_events=[tuple(xi for xi in x if xi is not None) for x in merge_events]
		
		#converting a python list to a string for display in attribute table
		events='/n'.join(map(str,merge_events))
		
	return events
'''


	arcpy.CalculateField_management(inputdataset,
                                    "Citation",
                                    'getCitation(!p_dataset_id!)', #dataset id has to be named as p_dataset_id in the geodatabase
                                    'PYTHON_9.3',
                                    expression)
									
	arcpy.CalculateField_management(inputdataset,
                                    "Projects",
                                    'getprojects(!p_dataset_id!)',
                                    'PYTHON_9.3')
									
	arcpy.CalculateField_management(inputdataset,
                                    "Events",
                                    'getevents(!p_dataset_id!)',
                                    'PYTHON_9.3')

import arcpy
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Pangaeapy"
        self.alias = "pangaeapy"
	
        # List of tool classes associated with this toolbox
        self.tools = [UpdateMetadata]


class UpdateMetadata(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update Metadata"
        self.description = "This toolbox get the metadata from the pangaeapy either by using a integer ID or an DOI of the dataset " + \
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
		
	#Second Parameter i.e., Option to get the dataset id from the geodatabase
	dataset_id = arcpy.Parameter(
		displayName="Dataset ID",
		name="dataset_id",
		datatype="Field",
		parameterType="Required",
		direction="Input")
		
	# Set the filter to accept only fields that are Long type
	dataset_id.filter.list = ['Long']
	dataset_id.parameterDependencies = [input_dataset.name]

	# Third Parameter
	output_dataset = arcpy.Parameter(
		displayName="Output Vector Dataset",
		name="output_dataset",
		datatype=["DEGeodatasetType"],
		parameterType="Derived",
		direction="Output")

	output_dataset.parameterDependencies = [input_dataset.name]
	#output_dataset.schema.clone = True

	params = [input_dataset, dataset_id, output_dataset]
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
	inputdataset = parameters[0].valueAsText
	datasetid = parameters[1].valueAsText
		
	arcpy.AddField_management(inputdataset, "citation", "TEXT" )
	arcpy.AddField_management(inputdataset, "label", "TEXT" )
	
	expression = '''
from pangaeapy import PanDataSet
def getCitation(p_dataset_id):
	ds=PanDataSet(p_dataset_id)
	return ds.citation
	
def geteventlabel(p_dataset_id):
	ds=PanDataSet(p_dataset_id)
	a=[]
	b=[]
	for proj in ds.projects:
		a.append(proj.label.text.strip())
		b.append(proj.name.text.strip())
		merge_label_name= [(a[i],b[i]) for i in range(0,len(a))]
		proj_label_name=','.join(map(str,merge_label_name))
	return proj_label_name
'''


	arcpy.CalculateField_management(inputdataset,
                                    "citation",
                                    'getCitation(!p_dataset_id!)',
                                    'PYTHON_9.3',
                                    expression)
									
	arcpy.CalculateField_management(inputdataset,
                                    "label",
                                    'geteventlabel(!p_dataset_id!)',
                                    'PYTHON_9.3')

"""
Author: Aarthi Balamurugan  
ArcGIS Pro version: 2.3
Python version: 3.6.6
"""
# -*- coding: utf-8 -*-
import arcpy
import os
import arcpy
import time
from arcpy import env
from pangaeapy import PanDataSet

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Update Metadata"
        self.alias = "UpdateMetadata"
	
        # List of tool classes associated with this toolbox
        self.tools = [UpdateMetadata]

class UpdateMetadata(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update Metadata"
        self.description = "This toolbox get the metadata from the pangaea dataset using pangaeapy module either by using a integer ID or an DOI of the dataset " + \
	"and updates the Geodatabase with a metadata."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        global projects, events, license, campaign
        projects = ""
        events = ""
        license = ""
        campaign = ""

        # First Parameter i.e., Input geodatabase with feature class tracklines
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
        dataset_id.filter.list = ['Long','Short']
        dataset_id.parameterDependencies = [input_dataset.name]
        
        params = [input_dataset, dataset_id]
        return params

    def execute(self, parameters, messages):
        """The source code of the tool."""
		
        inputdataset = parameters[0].valueAsText #getting the parameters
        datasetid = parameters[1].valueAsText
        
        #If the fields are not already in the attribute table, add the fields
        
        fields = [f.name for f in arcpy.ListFields(inputdataset)]
        field_to_add = ["Citation","Permission","Projects","Events","Campaign","License"]
		
        if field_to_add[0] not in fields:
                #Define the field length if it is more than 255 characters
                arcpy.AddField_management(inputdataset, "Citation", "TEXT" ,field_length = 1000)
        if field_to_add[1] not in fields:
                arcpy.AddField_management(inputdataset, "Permission", "TEXT" ,field_length = 1000)
        if field_to_add[2] not in fields:
                arcpy.AddField_management(inputdataset, "Projects", "TEXT" ,field_length = 1000 )
        if field_to_add[3] not in fields:
                arcpy.AddField_management(inputdataset, "Events", "TEXT" ,field_length = 5000 )
        if field_to_add[4] not in fields:
                arcpy.AddField_management(inputdataset, "Campaign", "TEXT" ,field_length = 5000 )
        if field_to_add[5] not in fields:
                arcpy.AddField_management(inputdataset, "License", "TEXT" ,field_length = 1000 )
        else:
                arcpy.AddMessage("Added the fields")
				
        # Assigning the fields to work with in update cursor
        fields = [datasetid,"Citation","Permission","Projects","Events","Campaign","License"]

        #Function to get all the project attributes from the pangaea metadata
        def getprojects(ds):

                global projects
                
                def listOfTuples(l1,l2,l3):
                        return list(map(lambda x,y,z:(x,y,z),l1,l2,l3))
                
                """The toolbox is designed to the store the values in list form in python and it is converted to string format
                to display in the attribute table of geodatabase. Because the list format to store values in geodatabase is not supported."""
                # Tuple can't be displayed in the attribute table consecutively. So the values are converted to list.
                proj_label=[]
                proj_name=[]
                proj_URL=[]
                
                if ds.projects != []:
                        for proj in ds.projects:
                                #Both label and name are hypertext. To get the text of the element text.strip() is used.
                                if proj.label is not None:
                                        proj_label.append(proj.label.text.strip())
                                else:
                                        proj_label.append(None)
                                if proj.name is not None:
                                        proj_name.append(proj.name.text.strip())
                                else:
                                        proj_name.append(None)
                                if proj.URL is not None:
                                        proj_URL.append(proj.URL.text.strip())
                                else:
                                        proj_URL.append(None)
                                merge_projects=listOfTuples(proj_label,proj_name,proj_URL)
                                final_projects=[tuple(ele for ele in sub if ele != None) for sub in merge_projects]
                                
                                projects='{0}'.format(final_projects)
                else:
                        projects=""
                        
                return projects
        
        #Function to get all the event attributes from the pangaea metadata
        def getevents(ds):
        
                global events
                
                def listOfTuples(l1,l2,l3,l4,l5,l6,l7,l8,l9,l10):
                        return list(map(lambda a,b,c,d,e,f,g,h,i,j:(a,b,c,d,e,f,g,h,i,j),l1,l2,l3,l4,l5,l6,l7,l8,l9,l10))
                
                event_label=[]
                start_latitude=[]
                start_longitude=[]
                end_latitude=[]
                end_longitude=[]
                start_datetime=[]
                end_datetime=[]
                location=[]
                basis=[]
                device=[]
                
                if ds.events != []:
                        for eve in ds.events:
                                event_label.append(eve.label)
                                if eve.latitude is not None:
                                        start_latitude.append("Latitude Start:{}".format(eve.latitude))
                                else:
                                        start_latitude.append(None)
                                if eve.longitude is not None:
                                        start_longitude.append("Longitude Start:{}".format(eve.longitude))
                                else:
                                        start_longitude.append(None)
                                if eve.latitude2 is not None:
                                        end_latitude.append("Latitude End:{}".format(eve.latitude2))
                                else:
                                        end_latitude.append(None)
                                if eve.longitude2 is not None:
                                        end_longitude.append("Longitude End:{}".format(eve.longitude2))
                                else:
                                        end_longitude.append(None)
                                if eve.datetime is not None:
                                        start_datetime.append("Date/Time Start:{}".format(eve.datetime))
                                else:
                                        start_datetime.append(None)
                                if eve.datetime2 is not None:
                                        end_datetime.append("Date/Time End:{}".format(eve.datetime2))
                                else:
                                        end_datetime.append(None)
                                if eve.location is not None:
                                        location.append("Location:{}".format(eve.location))
                                else:
                                        location.append(None)
                                if eve.basis is not None:
                                        basis.append("Basis:{}".format(eve.basis))
                                else:
                                        basis.append(None)
                                if eve.device is not None:
                                        device.append("Device:{}".format(eve.device))
                                else:
                                        device.append(None)
                                merge_events=listOfTuples(event_label,start_latitude,start_longitude,end_latitude,end_longitude,start_datetime,end_datetime,location,basis,device)
                                final_events=[tuple(ele for ele in sub if ele != None) for sub in merge_events]
                                
                                events='{0}'.format(final_events)
                else:
                        events=""
                        
                return events
                
        #Function to get all the campaign details from the pangaea metadata
        def getcampaign(ds):
        
                global campaign
                merge_campaign = []
                
                if ds.events != []:
                        for eve in ds.events:
                                if eve.campaign.name is not None:
                                        merge_campaign.append("Campaign:{}".format(eve.campaign.name))
                                if eve.campaign.URI is not None:
                                        merge_campaign.append("{}".format(eve.campaign.URI))
                                if eve.campaign.start is not None:
                                        merge_campaign.append("Start Date:{}".format(eve.campaign.start))
                                if eve.campaign.end is not None:
                                        merge_campaign.append("End Date:{}".format(eve.campaign.end))
                                if eve.campaign.startlocation is not None:
                                        merge_campaign.append("Start Location:{}".format(eve.campaign.startlocation))
                                if eve.campaign.endlocation is not None:
                                        merge_campaign.append("End Location:{}".format(eve.campaign.endlocation))
                                if eve.campaign.BSHID is not None:
                                        merge_campaign.append("BSH ID:{}".format(eve.campaign.BSHID))
                                if eve.campaign.expeditionprogram is not None:
                                        merge_campaign.append("Expedition Program:{}".format(eve.campaign.expeditionprogram))
                                #merge_campaign=[name,URI,start,end,startlocation,endlocation,BSHID,expeditionprogram]
                                
                                #campaign='{0}'.format([campval for campval in merge_campaign if campval !=None])
                                campaign='{0}'.format(merge_campaign)
                else:
                        campaign=""
                        
                return campaign
        
        #Function to get the license attribute from the pangaea metadata
        def getlicense(ds):
        
                global license
                
                if ds.licenses != []:
                        for lic in ds.licenses:
                                if lic.label is not None:
                                        label = lic.label.text.strip()
                                if lic.name is not None:
                                        name = lic.name.text.strip()
                                if lic.URI is not None:
                                        URI = lic.URI.text.strip()
                        
                                license = '{0},{1},{2}'.format(label,name,URI)
                else:
                        license=""
                        
                return license
        
        """Update cursor to update the rows with the values. The metadata from the pangaea dataset using pangaeapy module"""
        with arcpy.da.UpdateCursor(inputdataset,fields) as cursor:
                rec=0
                start = time.time()
                oldrow = " "
                for row in cursor:
                        if (row[1] or row[2] or row[3] or row[4] or row[5] or row[6] is None) or (row[1] or row[2] or row[3] or row[4] or row[5] or row[6] == ""):
                                if oldrow is not None and oldrow[0] == row[0]:
                                        row[1] = row_citation
                                        row[2] = row_loginstatus
                                        row[3] = row_projects
                                        row[4] = row_events
                                        row[5] = row_campaign
                                        row[6] = row_license
                                        oldrow = row
                                        cursor.updateRow(row)
                                        continue
                                if oldrow[0] != row[0]:
                                        ds= PanDataSet(row[0])
                                        row_citation = ds.citation
                                        row_loginstatus = ds.loginstatus
                                        row_projects = getprojects(ds)
                                        row_events = getevents(ds)
                                        row_campaign = getcampaign(ds)
                                        row_license = getlicense(ds)
                                        row[1] = row_citation
                                        row[2] = row_loginstatus
                                        row[3] = row_projects
                                        row[4] = row_events
                                        row[5] = row_campaign
                                        row[6] = row_license
                                        cursor.updateRow(row)
                                        oldrow = row
                                        rec=rec+1
                                        if (rec % 59 == 0):
                                                end = time.time()
                                                if ((end-start) <= 30):
                                                        wait = end-start
                                                        time.sleep(33-wait)
                                                        start = time.time()
                                                        continue
                                                else:
                                                        start = time.time()
                                                        continue
    

# Toolbox
Update metadata python toolbox to work in arcgis

A toolbox created to update the metadata attributes in the geodatabase. 
The metadata attributes are gathered from the Pangaea website using the dataset id.

- Multiple values from the events list, projects list could not be retrieved. 
- So the toolbox is designed to the store the values in list form in python and it is converted to string format
  to display in the attribute table of geodatabase.
- Because the list format to store values in geodatabase is not supported.

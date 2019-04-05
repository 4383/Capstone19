#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import csv
import xml.etree.cElementTree as ET
import xml.dom.minidom
import time
import glob
import os
import OSMPythonToolsHandler as OSM
import AssociateNodesAndWays as ANW
import DB_eOSMGenerator as DB

'''
Store each node data received from OpenAddresses
OpenAddresses data is in CSV.
It is parsed to object.
'''
class Node():
    ###############################
    #Get rid of unused variables
    ###############################
    longitude = ""
    latitude = ""
    id = ""
    data={
        "addr:housenumber" : "",
        "addr:street" : "",
        "addr:unit" : "",
        "addr:city" : "",
        "addr:district" : "",
        "addr:reqion" : "",
        "addr:postcode" : ""

    }
    hash = ""

'''
Holds the coordinated within which OSM data has to be fetched
Values are calculated from OpenAddresses CSV
'''
class Coordinates():
    latMin = 90
    latMax = -90
    lonMin = 180
    lonMax = -180

def GetFilenameFromPath(path):
    pathArr = path.split("\\")
    fn = pathArr[len(pathArr)-1]
    fn = fn[:fn.index('.csv')]
    return(fn)

'''
Calculates the min/max latitude and longitude required for OSM data fetch
'''
def ResetBox(box, lon, lat):
    if lat<(box.latMin):
        box.latMin=lat
    if lat>box.latMax:
        box.latMax=lat
    if lon<box.lonMin:
        box.lonMin=lon
    if lon>box.lonMax:
        box.lonMax=lon

'''
OpenAddresses data is in CSV format.
Converts CSV data to Node objects

'''
def GetNodesFromCsv(path):
    global xml
    nodes = []
    box = Coordinates()
    with open(path, encoding="utf8") as csvfile:
        csvData = csv.reader(csvfile)
        next(csvData, None)  # Skips headers for each file

        for row in csvData:
            nodeObj = AssignRowToObject(row)
            if nodeObj.longitude and nodeObj.latitude and nodeObj.data['addr:housenumber'] and nodeObj.data[
                'addr:street'] and nodeObj.id:
                nodes.append(nodeObj)
                ResetBox(box,float(nodeObj.longitude),float(nodeObj.latitude))
        nodes.append(box)   #appends the coordinates object to nodes list
        return nodes


'''
                node = ET.SubElement(root, "node", id=nodeObj.id, version="1", lat=nodeObj.latitude, lon=nodeObj.longitude,
                                     t="enhancedOSM")
                for key, val in nodeObj.data.items():
                    if val:
                        ET.SubElement(node, "tag", k=key, v=val)

            xml = ET.ElementTree(root)
    opfn = fn + str(int(time.time()))
    #xml.write("%s.xml" % opfn)
    '''

'''
Assigns each row of the CSV file to the Node object
'''
def AssignRowToObject(row):
    nodeObj = Node()
    nodeObj.longitude = (row[0])
    nodeObj.latitude = (row[1])
    nodeObj.number = row[2]
    nodeObj.street = row[3]
    nodeObj.data['addr:housenumber'] = str(row[2])
    nodeObj.data['addr:street'] = (row[3])
    nodeObj.data['addr:unit'] = row[4]
    nodeObj.data['addr:city'] = row[5]
    nodeObj.data['addr:district'] = row[6]
    nodeObj.data['addr:reqion'] = row[7]
    nodeObj.data['addr:postcode'] = row[8]
    nodeObj.id = row[9]
    nodeObj.hash = row[10]
    return nodeObj

def Main():
    DB.CreateDBConnection()
    nodes=[]
    #path="S:/Course work/Spring 19/Garmin/Alpharetta GA/us/ga"
    path="S:/data/"
    for path in glob.glob(os.path.join(path, '*.csv')):
        '''Gets nodes data from Open Address'''
        nodes=GetNodesFromCsv(path)
        print(path)

    '''
    Gets ways data from OSM based on Lat/Lon values calculated from nodes
    Stores the data in DB
    '''
    OSM.GetOSMWaysData(nodes[-1])
    del nodes[-1]   #Remove coordinates object as we do not need it anymore

    '''Compare ways and nodes data and matches nodes with ways'''
    ANW.MatchNodesWithOSMWays(nodes)


if __name__== "__main__":
  Main()

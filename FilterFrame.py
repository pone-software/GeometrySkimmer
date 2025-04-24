from icecube import icetray, dataclasses, simclasses

class FilterFrame(icetray.I3Module):
    def __init__(self, ctx):
        super(FilterFrame, self).__init__(ctx)
        self.AddParameter("AllowedStrings", "List of allowed string IDs", [])

    def Configure(self):
        self.photon_map_key = "I3Photons"
        self.allowed_strings = set(self.GetParameter("AllowedStrings"))  # Convert to set for fast lookup
    
    def Geometry(self, frame):
        omgeo_map = frame["I3OMGeoMap"]
        filtered_omgeo_map = dataclasses.I3OMGeoMap()
        for omkey, omgeo in omgeo_map.items():
            if omkey.string in self.allowed_strings:
                filtered_omgeo_map[omkey] = omgeo
        frame.Replace("I3OMGeoMap",filtered_omgeo_map)
        
        newGeo = dataclasses.I3Geometry()
        newGeo.start_time = frame["I3Geometry"].start_time
        newGeo.end_time = frame["I3Geometry"].end_time
        newGeo.omgeo = filtered_omgeo_map
        frame.Replace("I3Geometry",newGeo)

        modgeo_map = frame["I3ModuleGeoMap"]
        filtered_modgeo_map = dataclasses.I3ModuleGeoMap()
        for modkey, modgeo in modgeo_map.items():
            if modkey.string in self.allowed_strings:
                filtered_modgeo_map[modkey] = modgeo
        frame.Replace("I3ModuleGeoMap",filtered_modgeo_map)

        subdet = frame["Subdetectors"]
        filtered_det = dataclasses.I3MapModuleKeyString()
        for modkey, string in subdet.items():
            if modkey.string in self.allowed_strings:
                filtered_det[modkey] = string
        frame.Replace("Subdetectors",filtered_det)
 
        self.PushFrame(frame)

    def DAQ(self,frame):
        if self.photon_map_key in frame:
            photon_map = frame[self.photon_map_key] #get photon list
            filtered_map = simclasses.I3CompressedPhotonSeriesMap()    #make empty list        
            
            for module_key, photon_vector in photon_map.items():
                if module_key.string in self.allowed_strings:

                    filtered_map[module_key] = photon_vector
            
            if(filtered_map): #only write frames with photons
                frame.Replace(self.photon_map_key,filtered_map)
                self.PushFrame(frame)
                

from icecube import icetray, dataclasses, simclasses

class FilterFrame(icetray.I3Module):
    def __init__(self, ctx):
        super(FilterFrame, self).__init__(ctx)
        self.AddParameter("AllowedStrings", "List of allowed string IDs", [])

    def Configure(self):
        self.photon_map_key = "I3Photons"
        self.allowed_strings = set(self.GetParameter("AllowedStrings"))  # Convert to set for fast lookup
   
    def replaceOMGeo(self, frame):
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
        
        return frame
    
    def replaceModGeo(self, frame):
        modgeo_map = frame["I3ModuleGeoMap"]
        filtered_modgeo_map = dataclasses.I3ModuleGeoMap()
        for modkey, modgeo in modgeo_map.items():
            if modkey.string in self.allowed_strings:
                filtered_modgeo_map[modkey] = modgeo
        frame.Replace("I3ModuleGeoMap",filtered_modgeo_map)
        
        return frame

    def replaceSubdet(self,frame):
        subdet = frame["Subdetectors"]
        filtered_det = dataclasses.I3MapModuleKeyString()
        for modkey, string in subdet.items():
            if modkey.string in self.allowed_strings:
                filtered_det[modkey] = string
        frame.Replace("Subdetectors",filtered_det)
        return frame

    def replaceCal(self,frame):
        ical = frame["I3Calibration"]
        filtered_domcal = dataclasses.Map_OMKey_I3DOMCalibration()
        for modkey, cal in ical.dom_cal.items():
            if modkey.string in self.allowed_strings:
                filtered_domcal[modkey] = cal
        
        newcal = dataclasses.I3Calibration()
        newcal.dom_cal = filtered_domcal
        newcal.start_time = ical.start_time
        newcal.end_time = ical.end_time
        newcal.vem_cal = ical.vem_cal
        frame.Replace("I3Calibration",newcal)
        return frame

    def replaceStatus(self,frame):
        idet = frame["I3DetectorStatus"]
        filtered_domstat = dataclasses.Map_OMKey_I3DOMStatus()
        for modkey, stat in idet.dom_status.items():
            if modkey.string in self.allowed_strings:
                filtered_domstat[modkey] = stat
        
        newdet = dataclasses.I3DetectorStatus()
        newdet.dom_status = filtered_domstat
        newdet.start_time = idet.start_time
        newdet.end_time = idet.end_time
        newdet.daq_configuration_name = idet.daq_configuration_name
        newdet.trigger_status = idet.trigger_status
        frame.Replace("I3DetectorStatus",newdet)
        return frame
        
    
    def Geometry(self, frame):

        frame = self.replaceOMGeo(frame)
        frame = self.replaceModGeo(frame)
        frame = self.replaceSubdet(frame)
 
        self.PushFrame(frame)

    def Calibration(self, frame):
       
        frame = self.replaceOMGeo(frame)
        frame = self.replaceModGeo(frame)
        frame = self.replaceSubdet(frame)
        frame = self.replaceCal(frame) 
        
        self.PushFrame(frame)
    
    def DetectorStatus(self, frame):
       
        frame = self.replaceOMGeo(frame)
        frame = self.replaceModGeo(frame)
        frame = self.replaceSubdet(frame)
        frame = self.replaceCal(frame) 
        frame = self.replaceStatus(frame)
 
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
                

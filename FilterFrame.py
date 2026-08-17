from icecube import icetray, dataclasses, simclasses

class FilterFrame(icetray.I3Module):
    def __init__(self, ctx):
        super(FilterFrame, self).__init__(ctx)
        self.AddParameter("AllowedStrings", "List of allowed string IDs", [])
        self.AddParameter("AllowedOMs", "List of allowed OM IDs", [])
        self.AddParameter("ModuleMap","Map of allowed strings to 1 indexed list")

    def Configure(self):
        self.map_key = "Physics_MCPEMap"
        self.allowed_strings = set(self.GetParameter("AllowedStrings"))  # Convert to set for fast lookup
        self.allowed_oms = set(self.GetParameter("AllowedOMs"))  # Empty means no OM filtering
        self.ModuleMap = self.BuildModuleMap()

    def BuildModuleMap(self):
        module_map = {}
        for new_string_idx, string_id in enumerate(sorted(self.allowed_strings), start=1):
            for new_om_idx, om_id in enumerate(sorted(self.allowed_oms), start=1):
                old_module = dataclasses.ModuleKey(string_id, om_id)
                new_module = dataclasses.ModuleKey(new_string_idx, new_om_idx)
                module_map[old_module] = new_module

        return module_map

    def _is_allowed_omkey(self, omkey):
        return omkey.string in self.allowed_strings and omkey.om in self.allowed_oms

    def _is_allowed_modulekey(self, modkey):
        return modkey.string in self.allowed_strings and modkey.om in self.allowed_oms
   
    def replaceOMGeo(self, frame):
        geometry = frame["I3Geometry"]
        omgeo_map = geometry.omgeo

        filtered_omgeo_map = dataclasses.I3OMGeoMap()
        for omkey, omgeo in omgeo_map.items():
            if self._is_allowed_omkey(omkey):
                filtered_omgeo_map[self.getNewKey(omkey)] = omgeo

        if "I3OMGeoMap" in frame:
            frame.Replace("I3OMGeoMap", filtered_omgeo_map)
        
        newGeo = dataclasses.I3Geometry()
        newGeo.start_time = geometry.start_time
        newGeo.end_time = geometry.end_time
        newGeo.omgeo = filtered_omgeo_map
        frame.Replace("I3Geometry", newGeo)
        
        return frame
    
    def replaceModGeo(self, frame):
        modgeo_map = frame["I3ModuleGeoMap"]
        filtered_modgeo_map = dataclasses.I3ModuleGeoMap()
        for modkey, modgeo in modgeo_map.items():
            if self._is_allowed_modulekey(modkey):
                filtered_modgeo_map[self.getNewModuleKey(modkey)] = modgeo
        frame.Replace("I3ModuleGeoMap", filtered_modgeo_map)
        
        return frame

    def replaceSubdet(self,frame):
        filtered_det = dataclasses.I3MapModuleKeyString()
        for modkey in frame["I3ModuleGeoMap"].keys():
            filtered_det[modkey] = "POM"
        frame.Replace("Subdetectors", filtered_det)
        return frame

    def replaceCal(self,frame):
        ical = frame["I3Calibration"]
        filtered_domcal = dataclasses.Map_OMKey_I3DOMCalibration()
        for omkey, cal in ical.dom_cal.items():
            if self._is_allowed_omkey(omkey):
                filtered_domcal[self.getNewKey(omkey)] = cal
        
        newcal = dataclasses.I3Calibration()
        newcal.dom_cal = filtered_domcal
        newcal.start_time = ical.start_time
        newcal.end_time = ical.end_time
        newcal.vem_cal = ical.vem_cal
        frame.Replace("I3Calibration", newcal)
        return frame

    def replaceStatus(self,frame):
        idet = frame["I3DetectorStatus"]
        filtered_domstat = dataclasses.Map_OMKey_I3DOMStatus()
        for omkey, stat in idet.dom_status.items():
            if self._is_allowed_omkey(omkey):
                filtered_domstat[self.getNewKey(omkey)] = stat
        
        newdet = dataclasses.I3DetectorStatus()
        newdet.dom_status = filtered_domstat
        newdet.start_time = idet.start_time
        newdet.end_time = idet.end_time
        newdet.daq_configuration_name = idet.daq_configuration_name
        newdet.trigger_status = idet.trigger_status
        frame.Replace("I3DetectorStatus", newdet)
        return frame
        
    def getNewKey(self, oldkey):
        mapped_key = self.ModuleMap[dataclasses.ModuleKey(oldkey.string,oldkey.om)]
        return icetray.OMKey(mapped_key.string, mapped_key.om, oldkey.pmt)

    def getNewModuleKey(self, oldkey):
        mapped_key = self.ModuleMap[dataclasses.ModuleKey(oldkey.string, oldkey.om)]
        return dataclasses.ModuleKey(mapped_key.string, mapped_key.om)
    
    def Geometry(self, frame):

        frame = self.replaceOMGeo(frame)
        frame = self.replaceModGeo(frame)
        frame = self.replaceSubdet(frame)
 
        self.PushFrame(frame)

    def Calibration(self, frame):
        frame = self.replaceCal(frame) 
        
        self.PushFrame(frame)
    
    def DetectorStatus(self, frame):
        frame = self.replaceStatus(frame)
 
        self.PushFrame(frame)

    def DAQ(self,frame):
        if self.map_key in frame:
            mcpe_map = frame[self.map_key] #get mcpes
            filtered_map = simclasses.I3MCPESeriesMap()    #make empty list        
            
            for module_key, obj_vector in mcpe_map.items():
                if module_key.string in self.allowed_strings and module_key.om in self.allowed_oms:
                    filtered_map[self.getNewKey(module_key)] = obj_vector
            
            if(filtered_map): #only write frames with photons
                frame.Replace(self.map_key,filtered_map)
                self.PushFrame(frame)
                

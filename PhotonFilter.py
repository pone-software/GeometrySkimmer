from icecube import icetray, dataclasses, simclasses

class FilterPhotonList(icetray.I3Module):
	def __init__(self, ctx):
		super(FilterPhotonList, self).__init__(ctx)
		self.AddParameter("PhotonMapKey", "Key for the photon map in the frame", "I3Photons")
		self.AddParameter("AllowedStrings", "List of allowed string IDs", [])

	def Configure(self):
		self.photon_map_key = self.GetParameter("PhotonMapKey")
		self.allowed_strings = set(self.GetParameter("AllowedStrings"))  # Convert to set for fast lookup

	def Process(self):
		frame = self.PopFrame()
		if not frame:
			return
		if self.photon_map_key in frame:
			photon_map = frame[self.photon_map_key] #get photon list
			filtered_map = simclasses.I3CompressedPhotonSeriesMap()	#make empty list		
			
			for module_key, photon_vector in photon_map.items():
				if module_key.string in self.allowed_strings:

					filtered_map[module_key] = photon_vector
			
			if(filtered_map): #only write frames with photons
				frame.Replace(self.photon_map_key,filtered_map)
				self.PushFrame(frame)
				

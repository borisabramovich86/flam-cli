class Musician:
	def __init__(self, label, check_artist_label, display_text):
	    self.label = label
	    self.check_artist_label = check_artist_label
	    self.display_text = display_text
	    self.found = False
	    self.names = []
	    self.spotify_uris = []

class Drummer(Musician):
  def __init__(self):
    Musician.__init__(self, "Drums", "drummer", "Drummer - ")

class Bassist(Musician):
  def __init__(self):
    Musician.__init__(self, "Bass", "bassist", "Bassist - ")

class Keyboardist(Musician):
  def __init__(self):
    Musician.__init__(self, "Keyboards", "keyboardist", "Keyboardist - ")

class Guitarist(Musician):
  def __init__(self):
    Musician.__init__(self, "Guitar", "guitarist", "Guitarist - ")

class Vocals(Musician):
  def __init__(self):
    Musician.__init__(self, "Vocals", "singer", "Vocalist - ")
class ParamInfo(object):
    """
    Stores parameter information.
    """
    
    def __init__(self, name, loc, defval=None, value=None):
        self._name = name # parameter name
        self._default = defval # default value
        self._value = value # actual value to be used in a given ensemble member
        self._location = loc # location of parameter (params file or namelist)

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default
    
    @property
    def value(self):
        return self._value
    
    @property
    def location(self):
        return self._location
    
    @name.setter
    def name(self, new_name):
        self._name = new_name
        
    @default.setter
    def default(self, new_def):
        self._default = new_def
        
    @value.setter
    def value(self, new_val):
        self._value = new_val
            
    def __repr__(self):
        return "%s:\n\tloc = %s\n\tdefault = %s\n\tvalue = %s" % (self.name, self.location, self.default, self.value)

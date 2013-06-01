class OptionsError(Exception):
    pass

class Bunch(dict):
    """A dictionary that provides attribute-style access."""

    def __repr__(self):
        keys = list(self.keys())
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)
    
    def __getitem__(self, key):
        item = dict.__getitem__(self, key)
        if callable(item):
            return item()
        return item

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

class Namespace(Bunch):
    """A Bunch that will search dictionaries contained within to find a value.
    The search order is set via the order() method. See the order method for
    more information about search order.
    """
    def __init__(self, d=None, **kw):
        self._sections = []
        self._ordering = None
        self.update(d, **kw)
    
    def order(self, *keys, **kw):
        """Set the search order for this namespace. The arguments
        should be the list of keys in the order you wish to search,
        or a dictionary/Bunch that you want to search.
        Keys that are left out will not be searched. If you pass in
        no arguments, then the default ordering will be used. (The default
        is to search the global space first, then in the order in
        which the sections were created.)
        
        If you pass in a key name that is not a section, that
        key will be silently removed from the list.
        
        Keyword arguments are:
        
        add_rest=False
            put the sections you list at the front of the search
            and add the remaining sections to the end
        """
        if not keys:
            self._ordering = None
            return
        
        order = []
        for item in keys:
            if isinstance(item, dict) or item in self._sections:
                order.append(item)
        
        if kw.get('add_rest'):
            # this is not efficient. do we care? probably not.
            for item in self._sections:
                if item not in order:
                    order.append(item)
        self._ordering = order
        
    def clear(self):
        self._ordering = None
        self._sections = []
        super(Namespace, self).clear()
    
    def setdotted(self, key, value):
        """Sets a namespace key, value pair where the key
        can use dotted notation to set sub-values. For example,
        the key "foo.bar" will set the "bar" value in the "foo"
        Bunch in this Namespace. If foo does not exist, it is created
        as a Bunch. If foo is a value, an OptionsError will be
        raised."""
        segments = key.split(".")
        obj = self
        segment = segments.pop(0)
        while segments:
            if segment not in obj:
                obj[segment] = Bunch()
            obj = obj[segment]
            if not isinstance(obj, dict):
                raise OptionsError("In setting option '%s', %s was already a value"
                                   % (key, segment))
            segment = segments.pop(0)
        obj[segment] = value
    
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            self._sections.insert(0, key)
        super(Namespace, self).__setitem__(key, value)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def __getitem__(self, key):
        order = self._ordering
        if order is None:
            order = self._sections
        try:
            return super(Namespace, self).__getitem__(key)
        except KeyError:
            pass
        for section in order:
            if isinstance(section, dict):
                try:
                    return section[key]
                except KeyError:
                    pass
            else:
                try:
                    return self[section][key]
                except KeyError:
                    pass
        raise KeyError("Key %s not found in namespace" % key)
    
    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self[key] = value
    
    def __delitem__(self, key):
        try:
            index = self._sections.index(key)
            del self._sections[index]
        except ValueError:
            pass
        super(Namespace, self).__delitem__(key)
    
    def update(self, d=None, **kw):
        """Update the namespace. This is less efficient than the standard 
        dict.update but is necessary to keep track of the sections that we'll be
        searching."""
        items = []
        if d:
            # look up keys even though we call items
            # because that's what the dict.update
            # doc says
            if hasattr(d, 'keys'):
                items.extend(list(d.items()))
            else:
                items.extend(list(d))
        items.extend(list(kw.items()))
        for key, value in items:
            self[key] = value
    
    __call__ = update
    
    def setdefault(self, key, default):
        if not key in self:
            self[key] = default
            return default
        return self[key]

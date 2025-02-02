'''
Utils
=====

'''

__all__ = ('is_mobile_platform', 'intersection', 'difference', 'curry', 'strtotuple',
           'get_color_from_hex', 'get_random_color',
           'is_color_transparent', 'boundary', 'dist',
           'deprecated', 'SafeList',
           'interpolate', 'OrderedDict', 'kvFind', 'kvFindClass', 'kvPrintAttr',
           'breadth_first', 'walk_tree', 'filter_tree', 'kvquery', 'pct_h', 'pct_w', 'time_to_epoch')

import time
import calendar
from re import match, split
from UserDict import DictMixin
from kivy.core.window import Window
from kivy import platform
from datetime import datetime

def is_mobile_platform():
    return True if platform == 'android' or platform == 'ios' else False
    
def pct_h(pct):
    return Window.height * pct

def pct_w(pct):
    return Window.width * pct

def dist((x1, y1), (x2, y2)):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 5

def boundary(value, minvalue, maxvalue):
    '''Limit a value between a minvalue and maxvalue'''
    return min(max(value, minvalue), maxvalue)

def time_to_epoch(timestamp):
    return int(calendar.timegm(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").timetuple()))
    
def intersection(set1, set2):
    '''Return intersection between 2 list'''
    return filter(lambda s: s in set2, set1)


def difference(set1, set2):
    '''Return difference between 2 list'''
    return filter(lambda s: s not in set2, set1)

def curry(fn, *cargs, **ckwargs):
    '''Change the function signature to pass new variable.'''

    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn

def interpolate(value_from, value_to, step=10):
    '''Interpolate a value to another. Can be useful to smooth some transition.
    For example ::

        # instead of setting directly
        self.pos = pos

        # use interpolate, and you'll have a nice transition
        self.pos = interpolate(self.pos, new_pos)

    .. warning::
        This interpolation work only on list/tuple/double with the same
        dimension. No test are done if the dimension is not the same.
    '''
    if type(value_from) in (list, tuple):
        out = []
        for x, y in zip(value_from, value_to):
            out.append(interpolate(x, y, step))
        return out
    else:
        return value_from + (value_to - value_from) / float(step)


def strtotuple(s):
    '''Convert a tuple string into tuple,
    with some security check. Designed to be used
    with eval() function ::

        a = (12, 54, 68)
        b = str(a)         # return '(12, 54, 68)'
        c = strtotuple(b)  # return (12, 54, 68)

    '''
    # security
    if not match('^[,.0-9 ()\[\]]*$', s):
        raise Exception('Invalid characters in string for tuple conversion')
    # fast syntax check
    if s.count('(') != s.count(')'):
        raise Exception('Invalid count of ( and )')
    if s.count('[') != s.count(']'):
        raise Exception('Invalid count of [ and ]')
    r = eval(s)
    if type(r) not in (list, tuple):
        raise Exception('Conversion failed')
    return r


def get_color_from_hex(s):
    '''Transform from hex string color to kivy color'''
    if s.startswith('#'):
        return get_color_from_hex(s[1:])

    value = [int(x, 16)/255. for x in split('([0-9a-f]{2})', s.lower()) if x != '']
    if len(value) == 3:
        value.append(1)
    return value


def get_random_color(alpha=1.0):
    ''' Returns a random color (4 tuple)

    :Parameters:
        `alpha` : float, default to 1.0
            if alpha == 'random' a random alpha value is generated
    '''
    from random import random
    if alpha == 'random':
        return [random(), random(), random(), random()]
    else:
        return [random(), random(), random(), alpha]


def is_color_transparent(c):
    '''Return true if alpha channel is 0'''
    if len(c) < 4:
        return False
    if float(c[3]) == 0.:
        return True
    return False


DEPRECATED_CALLERS = []


def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted the first time
    the function is used.'''

    import inspect
    import functools

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        file, line, caller = inspect.stack()[1][1:4]
        caller_id = "%s:%s:%s" % (file, line, caller)
        # We want to print deprecated warnings only once:
        if caller_id not in DEPRECATED_CALLERS:
            DEPRECATED_CALLERS.append(caller_id)
            warning = (
                'Call to deprecated function %s in %s line %d.'
                'Called from %s line %d'
                ' by %s().') % (
                func.__name__,
                func.func_code.co_filename,
                func.func_code.co_firstlineno + 1,
                file, line, caller)
            from kivy.logger import Logger
            Logger.warn(warning)
            if func.__doc__:
                Logger.warn(func.__doc__)
        return func(*args, **kwargs)
    return new_func


class SafeList(list):
    '''List with clear() method

    .. warning::
        Usage of iterate() function will decrease your performance.
    '''

    def clear(self):
        del self[:]

    @deprecated
    def iterate(self, reverse=False):
        if reverse:
            return reversed(iter(self))
        return iter(self)


class OrderedDict(dict, DictMixin):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__end
        except AttributeError:
            self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items, ), inst_dict)
        return self.__class__, (items, )

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__, )
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return len(self)==len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other


def kvPrintAttr(w, k):
    print 'kvPrintAttr ' + str(w) + ' ',
    if hasattr(w, k):
        print(getattr(w, k))
    else:
        print 'None'
    for c in w.children:
        kvPrintAttr(c, k)
        
def kvFindClass(w, k):
    matched = []
    if issubclass(type(w), k):
        matched.append(w)
        
    for child in w.children:
        matched.extend(kvFindClass(child, k))
        
    return matched
    
def kvFind(w, k, v):
    #print "kvFind " + str(w) + " for " + k + ':' + v ,
    if hasattr(w, k):
        att = getattr(w, k, None)
      #  print("= " + str(att)),
        if v == att:
     #       print ' found ' + k + ':' + v + '! ' + str(w)
            return w

    #print 'searching children for ' + k + ':' + v 
    for child in w.children:
     #   print '\nsearching child ' + str(child) + ' of ' + str(w) + ' for ' + k + ':' + v 
        foundWidget = kvFind(child, k, v)
        if foundWidget:
            return foundWidget
    return None

def breadth_first(root, children=iter):
    '''walk tree is a generator function for breadth first tree traversal.
    it will traverse the entire decendant tree of a widget/node.

    example:
        #can be used in standard list comnprehension
        specials = [w for w in walk_tree(root) if 'special' in w.cls]

        #but doesnt generate whole list, if used with e.g. next()
        #will only go until 1 item is found
        first = (w for w in walk_tree(root) if 'special in w.cls').next()

        :Parameters:
        `root`: root of teh tree to be walked
            this node be the first node visited.

        `children`: function, default: iter
            function used to get an iterator over the nodes child nodes
    '''
    yield root
    last = root
    for node in breadth_first(root, children):
        for child in children(node):
            yield child
            last = child
        if last == node:
            return


def walk_tree(root):
    '''returns an iterator that walks a tree of objects which have
    a attribute named 'children', which defines the tree structure
    using breadth first search.

    example:
        w = Widget()
        for i in range(10):
            layout = BoxLayout()
            layout.add_widget(Button())
            layout.add_widget(Button())
            w.add_widget(layout)

        tree = walk_tree(w) # this is a generator function
        tree.next() # returns the first Boxlayout
        tree.next() # returns the second Boxlayout (breadth first)
        for w in tree:  #iterate over teh whole collection
            print w

    :Parameters:
    `root`: root of the tree to be walked
        this node be the first node visited.
    '''
    return breadth_first(root, lambda w: w.children)


def filter_tree(root, predicate):
    '''filter a tree based on a predecate.
    the filter_tree function is very simmilar to walk_tree,
    with teh excpetion, that will will skip all those nodes
    for which predicate(node) returns False.

    :Parameters:
    `root`: root of the tree to be walked
        this node be the first node visited.
    '''
    return (c for c in walk_tree(root) if predicate(c))


def kvquery(root, **kwargs):
    '''kvquery provides a convinient way of finding widgets in an
    application that uses the kv style language.

    example:
        lets say you have a .kv file with the following Rule:
        <MovieWidget>:
            BoxLayout:
                Video:
                    kvid: 'video'
                Label:
                    text: root.movie_title
                Label:
                    text: root.movie_description

        in your python code, you may want to get the reference to
        Video widget nested inside the widget you have a handle to.

        # video will be the first node that jas a 'kvid' property == 'video'
        video = kvquery(movie, kvid='video').next()


        #lets get all teh labels in a list
        labels = list(kvquery(movie, __class__=Label))


    :Parameters:
    `root`: root of the tree to queried
        this node and all decendants will be iterated by the
        returned generator.

    `**kwargs`: **kwargs, key/value pairs
        The keys corrosponf to porperty names, and values to the
        property values of the widget nodes being queried.  If a node
        has at least one attr such that (gettattr(node, key) == value)
        is true; it will be included in the iteration.
    '''

    def _query(w):
        '''iternal query function / predicate for tree query
        '''
        for k, v in kwargs.iteritems():
            if (v == getattr(w, k, None)):
                return True


    return filter_tree(root, _query)

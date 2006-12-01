# Copyright (c) 2005, the Lawrence Journal-World
# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Django nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Cache that uses the Berkeley Source Database.''' 

import bsddb
import time
try:
    from cStringIO import StringIO
except ImportError:
    from cStringIO import StringIO
try:
    import cPickle as pickle
except ImportError:
    import pickle
from shove.cache.memory import MemoryCache

__all__ = ['BsdbCache']


class BsdbCache(MemoryCache):

    '''Class for cache that uses the Berkeley Source Database.'''    

    def __init__(self, engine, **kw):
        super(BsdbCache, self).__init__(engine, **kw)
        self._cache = bsddb.hashopen(engine.split('/', 2))
        
    def __getitem__(self, key):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        local = StringIO(super(BsdbCache, self)[key])
        exp, now = pickle.load(local), time.time()
        # Remove item if time has expired.
        if exp < now: del self[key]
        return pickle.load(local)
                
    def __setitem__(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.        
        '''
        if len(self._cache) > self._max_entries: self._cull()
        local = StringIO()
        pickle.dump(time.time() + self.timeout, local, 2)
        pickle.dump(value, local, 2)
        super(BsdbCache, self)[key] = local.getvalue()
#
#    Copyright (C) 2002-2018  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# deprecated stuff (for ZODB/import/export)....
import logging, sys

from OFS.SimpleItem import SimpleItem

log = logging.getLogger('BLObserver [DEPRECATED]')


class BLObserverSupport(SimpleItem):
    """
    these guys need __new__
    """
    def manage_afterAdd(self, item, container):
        log.error(self.absolute_url())
        log.error(container.absolute_url())


class BLObserverOnAdd(BLObserverSupport):
    pass


class BLObserverOnChange(BLObserverSupport):
    pass


class BLObserverOnDelete(BLObserverSupport):
    pass



class zoproxy(SimpleItem):

    def __setstate__(self, state):
        pass
    
    def __of__(self, parent):
        pass

# some crappy acl_users lying around ...
#sys.modules['Products.BastionStore.BastionUserUserFolder.BastionUserUserFolder'] = zoproxy


#def repair(ledger):
#    for sub in ledger.ledgerValues():
#        # hmmm TODO - remove observer items ...
#        pass

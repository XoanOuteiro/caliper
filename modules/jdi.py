'''
-- Caliper
-- author/s: @XoanOuteiro
'''

from utils.reqhandler import ReqHandler
from utils.utilities import Utilities

'''
Handle logic for binary search of minimum ammount of
Junk Data Injection needed to bypass a WAF
'''
class JDIHandler:

    '''
    --- Instance Attributes ---
    '''
    request_item = None # ReqHandler instance that contains the user-provided request data (post-parsed)
    min_size = None # The minimum amount of junk data to be used
    max_size = None # The maximum amount of data to be used
    
    '''
    --- Constructors ---
    '''
    def __init__(self,request_item,min_size,max_size):
        self.request_item = request_item

        if min_size >= max_size:
            Utilities.print_error_msg("MIN_SIZE cannot be >= MAX_SIZE")
        else:
            self.min_size = min_size
            self.max_size = max_size
        Utilities.print_success_msg("JDI module instanced, starting...")


    '''
    --- Instance Methods ---
    '''


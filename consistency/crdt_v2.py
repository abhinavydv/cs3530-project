H = 0 # universal clock
uid = 444 # unique user id for each user within the group (mac/ip addr (within our LAN))

lowest_priority = -1 ## replace with -inf ?
highest_priority = 10000 ## replace with +inf ? => all uid's should be lesser than this

# single character for now => check how words work
class Wcharacter:
    """
        single element in the CRDT
        id: identifier i.e a tuple (uid, clock)
        value: element value eg. 'a' for a character
        visible: True/False i.e whether to display the element
        cp: id of the previous element
        cn: id of the next element
    """
    def __init__(self, id: tuple, val: str, visible: bool, prev: tuple, next: tuple) -> None: # O(1)
        """
            id: an identifier i.e a tuple (uid, clock)
            val: the character/element
            visible: True if the character should be visible
            prev: id of the previous element
            next: id of the next element
        """
        self.id = id 
        self.value = val
        self.visible = visible 
        self.cp = prev
        self.cn = next
    def __str__(self): # O(1)
        return f'< {self.id}, {self.value}, {self.visible}, {self.cp}, {self.cn} >'

# list of Wcharacters
# n = total no. of characters (including deleted)
class WString:
    def __init__(self): # O(1)
        cb = Wcharacter((lowest_priority, -1), 'cb', False, 1, 2)
        ce = Wcharacter((highest_priority, -1), 'ce', False, 1, 2)
        self.S = [cb, ce] # two default cb, ce for beginning and end
        
    
    def __str__(self):  # O(n) => ORDERED_TRAVERSAL

        str_list = []

        for i in self.S:
            str_list.append(str(i))
        
        output = ''.join(str_list)

        return output

    # Returns the visible string 
    def value(self): # O(n) => ORDERED_TRAVERSAL

        str_list = []
        for i in self.S:
            if i.visible:
                str_list.append(i.value)

        output = ''.join(str_list)

        return output 

    # returns wchar at pos on the ui
    # return None if not there => check 
    def ithVisible(self, pos): # O(n) => ORDERED_TRAVERSAL
        j = 0
        for i in self.S:
            
            if i.visible:
                j = j + 1
            
            if j == pos:
                return i

        return None

    ## replace with id 
    def contains(self, wchar): # O(n) => ORDERED_TRAVERSAL
        
        if wchar is None:
            return False

        for i in self.S:
            if i.id == wchar.id:
                return True
        
        return False

    def CP(self, wchar): # O(n) => ORDERED_TRAVERSAL

        for w in self.S:
            if w.id == wchar.cp:
                return w

        return None 

    def CN(self, wchar): # O(n) => ORDERED_TRAVERSAL

        for w in self.S:
            if w.id == wchar.cn:
                return w

        return None 
    
    ## returns the index of wchar in S, None otherwise
    def pos(self, wchar): # O(n) => ORDERED_TRAVERSAL

        for i in range(0, len(self.S)):
            if wchar.id == self.S[i].id:
                return i
        
        return None # Not found in the list
    
    ## inserts wchar in index p
    def insert(self, wchar, p): # O(n) 

        if p < 0 or p > len(self.S)-1:
            print('Error: WString::insert: invalid p, index out of bounds')

        S_b =  self.S[0 : p]
        S_b.append(wchar)
        S_e = self.S[p:]
        self.S = S_b + S_e 

    ## returns sublist b/w c,d excluding c, d
    def subseq(self, c, d): # O(n)

        ci = self.pos(c)
        di = self.pos(d)

        if ci is None or di is None:
            print('Error: WString::subseq: c/d not present in WString')
            return None

        return self.S[ci+1:di]

    ## returns the no of visible chars
    def noOfVisible(self): # O(n)
        
        j = 0

        for i in self.S:
            if i.visible:
                j = j + 1

        return j

    def at(self, i): # O(1)

        if i == -1:
            return self.S[-1]

        if i < 0 or i > len(self.S)-1:
            print('Error: WString::at i is out of range')
            return None

        return self.S[i]

class CRDT(object):

    def __init__(self, gui) -> None:
        self.S = WString()
        self.gui = gui

    def insert(self, position: int, value: str) -> str: 

        global H
        H = H + 1

        ## make sure position is valid
        if position != 1:
            cp = self.S.ithVisible(position-1) 
        else:
            cp = self.S.at(0) # make sure cb doesn't shift anywhere in IntegrateIns

        if position == self.S.noOfVisible()+1:
            cn = self.S.at(-1) # make sure ce doesn't shift anywhere in IntegrateIns
        else:
            cn = self.S.ithVisible(position) 

        if cp is None or cn is None:
            print('Error: GenerateIns: cp/cn is not present') # will happen if position is not valid ?
            return

        wchar = Wcharacter((uid, H), value, True, cp.id, cn.id) 

        self.IntegrateIns(wchar, cp, cn) 

        diff = 'insert: ' + str(wchar)

        print(diff)

        return diff
    
    def get_text(self) -> str:
        return "Hello!!"

    def GenerateDel(self, pos):
        wchar = self.S.ithVisible(pos)
        self.IntegrateDel(wchar)
        diff = 'delete: ' + str(wchar) + ';'
        return diff

    def delete(self, start, end) -> str:
        ## assuming start, end are valid

        diff_list = []

        for i in range(end-start+1):
            s = self.GenerateDel(start) # start is the position of delete
            diff_list.append(s)

        diff = ''.join(diff_list)

        print(diff)

        return diff

    def update(self, data):
        self.gui.rerender(data, self.gui.get_cur_pos())
    
    def display(self) -> str:
        return self.text 
    
    def IntegrateIns(self, c, cp, cn): # O(n^2)
        S_prime  = self.S.subseq(cp, cn) 

        if len(S_prime) == 0:
            self.S.insert(c, self.S.pos(cn))
        else:
            L = [cp]

            cpi = self.S.pos(cp)
            cni = self.S.pos(cn)

            for w in S_prime:
                if self.S.pos(self.S.CP(w)) <= cpi and self.S.pos(self.S.CN(w)) >= cni:
                    L.append(w)
            
            L.append(cn)
            
            i = 1 

            while (i < len(L)-1) and (L[i].id < c.id):
                i = i+1
            
            self.IntegrateIns(c, L[i-1], L[i])


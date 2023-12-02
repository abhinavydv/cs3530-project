## Replace docstrings later ? TESTING LEFT DON'T INTEGRATE
## WOOT CRDT 
## check Idempotent proof
## Reliability needed since it puts off updates if not possible on state => advantage prevents interleaving
## alternative - LSEQ, Treedoc, LampPort => interleaving => updating a word

## if arrays => replace binary search only a few 100 characters => check how words will scale
## balanced binary search tree => efficient, order on ids

H = 0 # universal clock
uid = 444 # unique user id for each user within the group (mac/ip addr)

lowest_priority = -1 ## replace with -inf ?
highest_priority = 1000 ## replace with +inf ?

# single element for now
class Wcharacter:
    def __init__(self, id, val, visible, prev, next):
        self.id = id # a pair (uid, clock) 
        self.value = val
        self.visible = visible 
        self.cp = prev
        self.cn = next
    def __str__(self):
        return f'< {self.id}, {self.value}, {self.visible}, {self.cp}, {self.cn} >'

# put inside class ?
# def get_id(Wchar):
#     return Wchar.id
    
# list of Wcharacters
class WString:
    def __init__(self):
        cb = Wcharacter((lowest_priority, -1), 'cb', False, 1, 2)
        ce = Wcharacter((highest_priority, -1), 'ce', False, 1, 2)
        self.S = [cb, ce] # two default cb, ce for beginning and end
    
    def __str__(self):

        output = ''
        for i in self.S:
            output = output + f'{i}, \n'
        
        return output

    # Returns the visible string 
    def value(self):
        # sorted_string = sorted(self.S, key=get_id)
        output = ''
        for i in self.S:
            if i.visible:
                output = output + i.value

        return output 
    
    # returns wchar at pos on the ui
    # return None if not there => check 
    def ithVisible(self, pos): 
        # sorted_string = sorted(self.S, key=get_id) # no need to sort, replace 
        j = 0
        for i in self.S:
            
            if i.visible:
                j = j + 1
            
            if j == pos:
                return i

        return None

    ## replace with id 
    def contains(self, wchar):
        
        ## not needed ig => check None comparisons
        if wchar is None:
            return False

        for i in self.S:
            if i.id == wchar.id:
                return True
        
        return False

    def CP(self, wchar):

        for w in self.S:
            if w.id == wchar.cp:
                return w

        return None 

    def CN(self, wchar):

        for w in self.S:
            if w.id == wchar.cn:
                return w

        return None 
    
    ## returns the index of wchar in S, None otherwise
    def pos(self, wchar):

        for i in range(0, len(self.S)):
            if wchar.id == self.S[i].id:
                return i
        
        return None # Not found in the list
    
    ## inserts wchar in index p
    def insert(self, wchar, p):

        if p < 0 or p > len(self.S)-1:
            print('Error: WString::insert: invalid p')

        S_b =  self.S[0 : p]
        S_b.append(wchar)
        S_e = self.S[p:]
        self.S = S_b + S_e 

    ## returns sublist b/w c,d excluding c, d
    def subseq(self, c, d):

        ci = self.pos(c)
        di = self.pos(d)

        if ci is None or di is None:
            print('Error: WString::subseq: c/d not present in WString')
            return None

        return self.S[ci+1:di]

    ## returns the no of visible chars
    def noOfVisible(self):
        
        j = 0

        for i in self.S:
            if i.visible:
                j = j + 1
            
        return j

    def at(self, i):

        if i == -1:
            return self.S[-1]

        if i < 0 or i > len(self.S)-1:
            print('Error: WString::at i is out of range')
            return None

        return self.S[i]
    

## from network
class operation:
    def __init__(self, type, wchar):
        self.type = type
        self.char = wchar

## Here Ins stands for insert, del for delete

## pos - position where the character is visible - count from 1 eg: "xyz" pos of y = 2
## val - character => change to word after PROVE_LINEARITY
def GenerateIns(pos, val):
    global H
    H = H + 1
    ## make sure pos is valid
    if pos != 1:
        cp = S.ithVisible(pos-1) 
    else:
        cp = S.at(0) # make sure doesn't shift anywhere in IntegrateIns
    
    if pos == S.noOfVisible()+1:
        cn = S.at(-1) # make sure doesn't shift anywhere in IntegrateIns
    else:
        cn = S.ithVisible(pos) 

    if cp is None or cn is None:
        print('Error: GenerateIns: cp/cn is not present')
        return

    wchar = Wcharacter((uid, H), val, True, cp.id, cn.id) ## run after cb, ce reserved are added

    IntegrateIns(wchar, cp, cn) ## updates on the wstring
    ## broadcast ins(wchar) => as byte string

def GenerateDel(pos):
    wchar = S.ithVisible(pos)
    IntegrateDel(wchar)
    ## broadcast del(wchar) => as byte string

## To check if prev conditions satisfied ? => LSEQ didn't need this check
## op - string specifying the operation
def isExecutable(op):
    
    c = op.char
    if op.type == 'del':
        return S.contains(c)
    else:
        return (S.contains(S.CP(c)) and S.contains(S.CN(c)))

# Call on receiving an operation 
def Reception(op):
    pool.append(op)

def IntegrateDel(wchar):
    wchar.visible = False

def IntegrateIns(c, cp, cn):
    S_prime  = S.subseq(cp, cn) 

    if len(S_prime) == 0:
        S.insert(c, S.pos(cn))
    else:
        L = [cp]

        cpi = S.pos(cp)
        cni = S.pos(cn)

        for w in S_prime:
            if S.pos(S.CP(w)) <= cpi and S.pos(S.CN(w)) >= cni:
                L.append(w)
        
        L.append(cn)
        
        i = 1 

        while (i < len(L)-1) and (L[i].id < c.id):
            i = i+1
        
        IntegrateIns(c, L[i-1], L[i])


# testing
# def main():
#     while True:

S = WString() 
pool = [] # list of pending operations

print(S.value())
print(S)

GenerateIns(1, 'a')
print(S.value())
# print(S)


GenerateIns(2, 'b')
print(S.value())
# print(S)


GenerateIns(2, '1')
print(S.value())
# print(S)

GenerateIns(2, '3')
print(S.value())
# print(S)

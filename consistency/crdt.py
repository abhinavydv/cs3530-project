import y_py as Y

# add format 

class CRDT(object):

    def __init__(self, intial_state = None) -> None:
        self.doc = Y.YDoc()
        self.text = self.doc.get_text('filename')

        # for the first time connection
        if intial_state is not None:
            Y.apply_update(self.doc, intial_state)
        
    def insert(self, position: int, value: str) -> bytes: # is it bytes ?
        with self.doc.begin_transaction() as txn:
            self.text.insert(txn, position, str)
        diff = Y.encode_state_as_update(self.doc) # this increases bandwidth, alternative is 2 transactions
        return diff # broadcast this
        

    def delete(self, start, end) -> bytes:
        with self.doc.begin_transaction() as txn:
            self.text.delete_range(txn, start, end-start+1) # 3rd arg is # of char, end is being included
        diff = Y.encode_state_as_update(self.doc)
        return diff # broadcast
    
    def display(self) -> str:
        return self.text # there is some non-determinism .. still need to check
    
    

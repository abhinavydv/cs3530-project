import y_py as Y

# first user

d1 = Y.YDoc()

text = d1.get_text('test')

with d1.begin_transaction() as txn:
    text.insert(txn, 0, 'abc')

diff1 = Y.encode_state_as_update(d1) 

print(text)

d2 = Y.YDoc()

text2 = d2.get_text('test')

Y.apply_update(d2, diff1)

with d2.begin_transaction() as txn:
    text2.insert(txn, 0, 'hello ')

with d2.begin_transaction() as txn:
    text2.delete_range(txn, 0, 2)

diff2 = Y.encode_state_as_update(d2)
print(text2)


with d1.begin_transaction() as txn:
    text.insert(txn, 0, 'def')

print(text)

Y.apply_update(d1, diff2)

print(d1.get_text('test'))



# print(d1.get_text('test'))

# with d1.begin_transaction() as txn:
#     text.extend(txn, 'Bob, ')

# print(d1.get_text('test'))
# diff1 = Y.encode_state_as_update(d1)


# with d1.begin_transaction() as txn:
#     text.extend(txn, 'I was here')

# print(d1.get_text('test'))

# diff2 = Y.encode_state_as_update(d1)


# d2 = Y.YDoc()
# text2 =d2.get_text('test')

# Y.apply_update(d2, diff1)

# # with d2.begin_transaction() as txn:
# #     text2.extend(txn, 'Bob, ')

# print(d2.get_text('test'))

# with d2.begin_transaction() as txn:
#     text2.extend(txn, ' la la la')

# print(d2.get_text('test'))

# # state_vector = Y.encode_state_vector(d2)

# # print(state_vector) # byte string

# Y.apply_update(d2, diff2)

# print(d2.get_text('test'))

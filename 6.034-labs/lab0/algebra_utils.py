"""
These are functions for transferring algebra.py's test cases over the
Internet. You shouldn't need to mess with these.
"""
from algebra import simplify_if_possible, Sum, Product, Expression

def distribution(val):
    if isinstance(val, Expression):
        raise ValueError("expression has already been decoded")
    return encode_sumprod(simplify_if_possible(decode_sumprod(val)))

def encode_sumprod(lst):
    retVal = []

    if isinstance(lst, Sum):
        retVal.append('Sum')
    elif isinstance(lst, Product):
        retVal.append('Product')

    for elt in lst:
        if isinstance(elt, (Sum, Product)):
            retVal.append( encode_sumprod(elt) )
        else:
            retVal.append(elt)

    return retVal


def decode_sumprod(lst):
    retVal = []

    for elt in lst[1:]:
        if isinstance(elt, (list, tuple)):
            retVal.append(decode_sumprod(elt))
        else:
            retVal.append(elt)

    if lst[0] == 'Sum':
        retVal = Sum(retVal)
    elif lst[0] == 'Product':
        retVal = Product(retVal)
    else:
        raise Exception, "Error: List was not an encoded Sum or Product!"
    
    return retVal



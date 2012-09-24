# template for 6.02 rectangular parity decoding using error triangulation
import PS2_tests
import numpy

def rect_parity(codeword,nrows,ncols): 
    counter = 0
    row_sums = [0 for i in xrange(nrows)]
    column_sums = [0 for i in xrange(ncols)]
    for i in xrange(nrows):
        for j in xrange(ncols):
            row_sums[i] += codeword[counter]
            column_sums[j] += codeword[counter]
            counter += 1
    row_errors = []
    column_errors = []
    broken_bits = 0
    for i in xrange(nrows):
        if (row_sums[i] % 2) != codeword[nrows*ncols+i]:
            row_errors.append(i)
    for j in xrange(ncols):
        if (column_sums[j] % 2) != codeword[nrows*ncols+nrows+j]:
            column_errors.append(j)
    result = [codeword[k] for k in xrange(len(codeword)) if k <= (nrows*ncols-1)]
    if len(row_errors) == 1 and len(column_errors) == 1:
        result[row_errors[0]*ncols+column_errors[0]] = (result[row_errors[0]*ncols+column_errors[0]] + 1) % 2
    return result

if __name__ == '__main__':
    PS2_tests.test_correct_errors(rect_parity)


# The 'NN' constructor takes three arguments:
# - Num of input nodes
# - Num of hidden nodes
# - Num of output nodes
# It returns an instance of the 'NN' (Neural Net) class with random (even distribution between 0.0 and 2.0) initial node weights.
from bpnn import NN as generate_net

#def generate_xor_net():
#    """ Generate a network intended for matching against XOR """
#    from bpnn import NN
#    return NN(2, 2, 1)

XOR_EXAMPLES = [ ([1.0,0.0],[1.0]), ([0.0,1.0],[1.0]), ([1.0,1.0],[0.0]), ([0.0,0.0],[0.0]) ]


def train_neural_net(net, examples, epoch_step_size = 100, learning_rate = 0.5,
momentum = 0.0, epsilon_error = 0.00001, max_train_epochs = 200000, verbose = False):
    """ Train a neural net.

    examples - A list of 2-tuples containing (in order) a list of inputs and a list of expected outputs, to be passed to the neural net for training purposes.
               For example, "[ ([1.0,0.0],[1.0]), ([1.0,1.0],[0.0]), ([0.0,1.0],[1.0]), ([0.0,0.0],[0.0]) ]" would be the set of examples for the 'XOR' function.
    epoch_step_size - The number of epochs to iterate through in between each check to see if the net has converged
    learning_rate - The learning rate of the neural net
    momentum - The momentum factor for the network.  Not used in 6.034.
    epsilon_error - The amount of change in error below which we decide that
    the neural net has stopped converging.
    max_train_epochs - The maximum number of epochs to try to train the net for, before giving up.  Must be a multiple of epoch_step_size.
    verbose = Set to 'True' if you want to see printed messages indicating how long it took the net to converge.

    Returns the number of iterations it took for the net to converge, or False if it did not converge.
    """
    started_converging = False

    prev_mean_err = None
    for count in xrange(max_train_epochs/epoch_step_size):
        mean_err = net.train(examples, iterations = epoch_step_size, N = learning_rate, M = momentum)
        if prev_mean_err is None: prev_mean_err = mean_err

        if abs(prev_mean_err-mean_err) < epsilon_error:
            if started_converging:
                if verbose:
                    print "Finished after %d epochs" %\
                    (count*epoch_step_size)

                return count            
        else:
            started_converging = True
        prev_mean_err = mean_err

        if verbose:
            print "%d epochs, with a mean error of %s" % (count*epoch_step_size, mean_err)

            
    if verbose:
        print "Failed to converge after %d epochs" % max_train_epochs

    return False


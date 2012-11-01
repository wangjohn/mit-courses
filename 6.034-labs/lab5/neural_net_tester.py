#!/usr/bin/env python2.5
#
# Unit tester for neural_net.py
#
import sys

from neural_net import train, test,\
     make_neural_net_basic,\
     make_neural_net_two_layer,\
     make_neural_net_challenging,\
     make_neural_net_with_weights

from neural_net_data import simple_data_sets,\
     harder_data_sets,\
     challenging_data_sets,\
     manual_weight_data_sets,\
     all_data_sets

def main(neural_net_func, data_sets, max_iterations=10000):
    verbose = True
    for name, training_data, test_data in data_sets:
        print "-"*40
        print "Training on %s data" %(name)
        nn = neural_net_func()
        train(nn, training_data, max_iterations=max_iterations,
              verbose=verbose)
        print "Trained weights:"
        for w in nn.weights:
            print "Weight '%s': %f"%(w.get_name(),w.get_value())
        print "Testing on %s test-data" %(name)
        result = test(nn, test_data, verbose=verbose)
        print "Accuracy: %f"%(result)

if __name__=="__main__":
    test_names = ["simple"]
    if len(sys.argv) > 1:
        test_names = sys.argv[1:]

    for test_name in test_names:
        if test_name == "simple":
            # these test simple logical configurations
            main(make_neural_net_basic,
                 simple_data_sets)

        elif test_name == "two_layer":
            # these test cases are slightly harder
            main(make_neural_net_two_layer,
                 simple_data_sets + harder_data_sets)

        elif test_name == "challenging":
            # these tests require a more complex architecture.
            main(make_neural_net_challenging, challenging_data_sets)

        elif test_name == "patchy":
            # patchy problem is slightly tricky
            # unless your network gets the right weights.
            # it can quickly get stuck in local maxima.
            main(make_neural_net_challenging, manual_weight_data_sets)

        elif test_name == "weights":
            # if you set the 'right' weights for
            # the patchy problem it can converge very quickly.
            main(make_neural_net_with_weights, manual_weight_data_sets,100)
        else:
            print "unrecognized test name %s" %(test_name)

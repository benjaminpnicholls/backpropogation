from random import randrange  # Used for random weights in network creation.
from math import exp  # Used for error calculations.
from tqdm import tqdm  # Used for the epoch progress bar.
from matplotlib import pyplot as plt  # Used to plot errors.

def main():
    # Customisable variables.
    epoch_count_master = 100
    learning_rate = 0.1
    hidden_layers_neuron_list = [3]
    filenames = ['data-assignment.txt', 'data-assignment-test.txt']

    ###### Random weights are overwritten in network_create() with given assignment weights. #####

    try:
        print('Enter filepath to data files (blank for current directory):')
        filepath = input('>>> ')
        # Append trailing / or \ for Mac/Windows, respectively.
        if '/' in filepath: 
            if (filepath[-1] != '/'): filepath += '/'
        if '\\' in filepath:
            if (filepath[-1] != '\\'): filepath += '\\'
    except:
        filepath = ''


    dataset = []
    targets = []
    for filename in filenames:
        filename = filepath + filename

        if 'test' in filename:
            test = True
            dataset, targets = parse_file(filename, dataset, targets, True)
            epoch_count = 1
            network_test(network, dataset)
            print_softmax(network)
        else:
            test = False
            dataset, targets = parse_file(filename, dataset, targets, False)
            epoch_count = epoch_count_master

            input_count = len(dataset[0])
            output_count = len(targets[0])

            layers_node_count = [input_count]
            for a in hidden_layers_neuron_list:
                layers_node_count.append(a)
            layers_node_count.append(output_count)

            print(f'\nTraining:\nLayers: {layers_node_count}, number of epochs: {epoch_count}, learning rate: {learning_rate}.\n')
            network = network_create(layers_node_count)
            network_train(network, dataset, targets, epoch_count, learning_rate, filename)
            network_test(network, dataset)

    return


def print_softmax(network):
    '''Prints the softmax values of the output layer neurons. No return.'''
    softmax = softmax_function(network[-1])
    print('softmax=', softmax)
    return


def network_create(layers_node_count):
    '''Returns a completed network double nested list with dictionaries inside with random weights (as a list) for each neuron connection.'''
    # Dynamic creation of a network with random weights with any number of hidden layers.
    network = []
    layer = []
    neuron = []
    for layer_index, network_layer in enumerate(layers_node_count):
        if (layer_index == 0 or layer_index == len(layers_node_count)): continue  # Input layer has no weights.
        for neuron_count in range(network_layer):
            for connection_count in range(layers_node_count[layer_index - 1] + 1):  # +1 for bias.
                neuron.append(randrange(-5, 5)/100)
            layer.append({'weights':neuron})
            neuron = []
        network.append(layer)
        layer = []

    # Assignment weights - overwrites random weights from above.
    if True:
        network =   [
                        [
                            {'weights': [0.74, 0.80, 0.35, 0.90]},
                            {'weights': [0.13, 0.40, 0.97, 0.45]},
                            {'weights': [0.68, 0.10, 0.96, 0.36]}
                        ],
                        [
                            {'weights': [0.35, 0.50, 0.90, 0.98]},
                            {'weights': [0.80, 0.13, 0.80, 0.92]}
                        ]
                    ]

    return network


def print_network_readable(network, epoch):
    '''Prints the network by neuron. Dictionary entries printed on one line each. No return.'''
    print('EPOCH=', epoch)
    for layer_index, layer in enumerate(network):
        for neuron_index, neuron in enumerate(layer):
            print('layer=', layer_index, ', neuron=', neuron_index)
            for key, values in neuron.items():
                print('\t\t', key, ': ', values)
            print('\n')
        print('\n')
    return


def network_train(network, dataset, targets, epoch_count, learning_rate, fileName):
    '''Trains the network using the dataset for the epoch count. Forward and then backpropogation. Errors are graphed. Returns network.'''
    error_list = []
    for epoch in tqdm(range(epoch_count)):
        error_squared_sum = 0
        for row_index, row in enumerate(dataset):
            forward_propogation(network, row)
            target = targets[row_index]
            backward_propogation(network, row, target, learning_rate)
            error_squared_sum += calculate_error_squared(network)
        error_list.append(error_squared_sum)
        name = fileName.split('/')[-1] +   '. Epochs= ' + str(epoch_count) + '. L= ' + str(learning_rate)
    plot_learning_curve(error_list, name)
    return network


def softmax_function(layer):
    '''Calculates the probability each output neuron has of being activated. Returns this as a list.'''
    sum = 0
    softmax_list = []
    for neuron_index, neuron in enumerate(layer):
        sum += exp(neuron['output'])
    for neuron_index, neuron in enumerate(layer):
        softmax = exp(neuron['output']) / sum
        softmax_list.append(softmax)
    return softmax_list


def calculate_error_squared(network):
    '''Sums squared errors from output layer of the network. Returns sum.'''
    error_squared = 0
    for output_neuron in network[-1]:
        error_squared += output_neuron['error']**2
    return error_squared


def plot_learning_curve(errors, name):
    '''Plots a graph of errors squared vs epoch. Graph is a popup. No return.'''
    x_data = []
    y_data = []
    x_data.extend(epoch for epoch in range(len(errors)))#epoch for epoch, data in enumerate(errors))
    y_data.extend(error for error in errors)
    fig, ax = plt.subplots()
    fig.suptitle(name)
    ax.set(xlabel='Epoch', ylabel='Squared Error')
    ax.plot(x_data, y_data, 'tab:green')
    plt.show()
    return


def backward_propogation(network, row, target, learning_rate):
    '''Backpropogation for the network. Network updates weights, errors, and deltas. Returns network.'''
    network.reverse()

    for layer_index, layer in enumerate(network):
        for neuron_index, neuron in enumerate(layer):
            deltas = []

            # Error calculation.
            if (layer_index == 0):  # if output layer:
                neuron['error'] = target[neuron_index] - neuron['output']
            else:  # Hidden layer, larger error calculation.
                sum = 0
                next_layer = network[layer_index - 1]  # Technically layer BEFORE in REVERSED network.
                for next_layer_neuron in next_layer:
                    sum += next_layer_neuron['weights'][neuron_index] * next_layer_neuron['error'] 
                neuron['error'] = neuron['output'] * (1 - neuron['output']) * ( sum )

            # First hidden layer needs input data to reference, otherwise use layer before.
            next_layer = row
            flag_first_hidden_layer = True
            if (layer_index + 1) < len(network):
                next_layer = network[layer_index + 1]
                flag_first_hidden_layer = False

            # Delta calculation.
            for next_layer_neuron in next_layer:
                if flag_first_hidden_layer:
                    input_value = next_layer_neuron
                else:
                    input_value = next_layer_neuron['output']
                delta = learning_rate * neuron['error'] * input_value
                deltas.append(delta)
            
            delta = learning_rate * neuron['error'] * 1  # Add bias delta.
            deltas.append(delta)
            neuron['deltas'] = deltas

    # Update weights throughout the network.
    for layer in network:
        for neuron in layer:
            for w in range(len(neuron['weights'])):
                neuron['weights'][w] += neuron['deltas'][w]

    network.reverse()
    return network


def activation(inputs, weights):
    '''Return summed dot products of inputs and weights.'''
    net = weights[-1]  # Use bias as the starting net--> no input data to multiply with.
    for a in range(len(inputs)):
        net += inputs[a] * weights[a]
    return net    


def sigmoid(x):
    '''Returns a value between -1 and 1.'''
    return 1 / (1 + exp(-x))


def forward_propogation(network, row):
    '''Returns the outputs from the network for this epoch.'''
    input = row
    for layer_index, layer in enumerate(network):
        input_next = []
        for neuron in layer:
            output = activation(input, neuron['weights'])
            if (layer_index < len(network) - 1):  # Output layer does not use sigmoid.
                output = sigmoid(output)  
            neuron['output'] = output
            input_next.append(neuron['output'])
        input = input_next
    return input  # The last "inputs" will actually be the outputs from the output neurons.
        

def network_test(network, dataset):
    '''Forward propogates through the network.'''
    print('\nTesting:')
    for row in dataset:
        output = forward_propogation(network, row)
        if (output[0] > output[1]):  # Only works for binary problems.
            output = 0
        else:
            output = 1
        print(f'input= {row} \t output= {output}')
    return network


def parse_file(filename, dataset, targets, isThisTestData):
    '''Parses file and returns dataset and targets nested lists.'''
    try:
        if '/' in filename:
            filename_temp = filename.split('/')[-1]
        elif '\\' in filename:
            filename_temp = filename.split('\\')[-1]
        else:
            filename_temp = filename
        f = open(filename_temp,'r')
        lines = f.readlines()
        filename = filename_temp  # Used to display success message.
    except FileNotFoundError:
        try:
            f = open(filename,'r')
            lines = f.readlines()
        except FileNotFoundError:
            print(f'\n\nFile \'{filename_temp}\' not found in current working directory or at location: {filename} \n\n')
            exit()
    
    dataset = []
    targets = []

    for line in lines:
        temp = line.split('\t')[0].split()
        for a in range(len(temp)):
            temp[a] = float(temp[a])
        dataset.append(temp)
        if (not isThisTestData):  # Test data has no targets in file.
            temp = line.split('\t')[1].split()
            for a in range(len(temp)):
                temp[a] = int(temp[a])
            targets.append(temp)
    print('\nUsing data from: ', filename)
    return dataset, targets


if __name__ == '__main__':
    main()
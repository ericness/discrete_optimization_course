#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple

from pyomo import environ as pe

Item = namedtuple("Item", ['index', 'value', 'weight'])


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

    model = pe.ConcreteModel()
    model.knapsack_items = pe.Set(
        initialize={item.index for item in items}
    )
    model.item_weights = pe.Param(
        model.knapsack_items,
        initialize={item.index: item.weight for item in items},
        within=pe.NonNegativeIntegers,
    )
    model.item_values = pe.Param(
        model.knapsack_items,
        initialize={item.index: item.value for item in items},
        within=pe.NonNegativeIntegers,
    )
    model.item_taken = pe.Var(
        model.knapsack_items,
        domain=pe.Binary,
    )
    model.objective = pe.Objective(
        expr=pe.summation(model.item_values, model.item_taken),
        sense=pe.maximize
    )
    model.total_weight = pe.Constraint(
        expr=sum(model.item_weights[i] * model.item_taken[i] for i in model.knapsack_items) <= capacity
    )
    solver = pe.SolverFactory("glpk")
    solver.solve(model)

    items_taken = model.item_taken.get_values()
    value = sum(model.item_values[index] for index, value in items_taken.items() if value == 1)
    taken = [int(value) for value in items_taken.values()]

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')


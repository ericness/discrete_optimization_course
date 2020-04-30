#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple

from pyomo import environ as pe

Edge = namedtuple("Edge", ['node1', 'node2'])


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    # build a trivial solution
    # every node has its own color
    model = pe.ConcreteModel()
    model.nodes = pe.Set(
        initialize=range(node_count),
        domain=pe.NonNegativeIntegers
    )
    model.edges = pe.Set(
        initialize={Edge(node1=edge[0], node2=edge[1]) for edge in edges},
    )
#    model.colors = pe.Set(initialize=range(10), domain=pe.NonNegativeIntegers)
    model.node_colors = pe.Var(
        model.nodes,
#        model.colors,
        domain=pe.NonNegativeIntegers,
        initialize=0,
    )
    model.max_color = pe.Var(domain=pe.PositiveIntegers)

    model.objective = pe.Objective(
        expr=model.max_color,
        sense=pe.minimize
    )

    def minimize_color(model, color: pe.NonNegativeIntegers, node: pe.NonNegativeIntegers):
        return model.max_color >= color * model.node_colors[node, color]

    model.minimize_color = pe.Constraint(model.colors, model.nodes, rule=minimize_color)

    def neighbor_colors(model, color: pe.NonNegativeIntegers, edge: Edge):
        return model.node_colors[edge.node1, color] + model.node_colors[edge.node2, color] <= 1

    model.neighbor_colors = pe.Constraint(model.colors, model.edges, rule=neighbor_colors)

    def one_color(model, node: pe.NonNegativeIntegers):
        return sum(model.node_colors[node, color] for color in model.colors) == 1

    model.one_color = pe.Constraint(model.nodes, rule=one_color)

    solver = pe.SolverFactory("cbc")
    solver.solve(model)

    solution = []
    for node in model.nodes:
        for color in model.colors:
            if model.node_colors[node, color] == 1:
                solution.append(color)

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')


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
    color_limit = int(node_count/4)

    model = pe.ConcreteModel()
    model.nodes = pe.Set(
        initialize=range(node_count),
        domain=pe.NonNegativeIntegers
    )
    model.edges = pe.Set(
        initialize={Edge(node1=edge[0], node2=edge[1]) for edge in edges},
    )
    model.colors = pe.Set(initialize=range(color_limit), domain=pe.NonNegativeIntegers)
    model.node_colors = pe.Var(
        model.nodes,
        model.colors,
        domain=pe.Binary,
        initialize=0,
    )
    model.color_used = pe.Var(model.colors, domain=pe.Binary)

    model.objective = pe.Objective(
        expr=pe.summation(model.color_used),
        sense=pe.minimize
    )

    def neighbor_colors(model, color: pe.NonNegativeIntegers, edge: Edge):
        return model.node_colors[edge.node1, color] + model.node_colors[edge.node2, color] <= model.color_used[color]

    model.neighbor_colors = pe.Constraint(model.colors, model.edges, rule=neighbor_colors)

    def one_color(model, node: pe.NonNegativeIntegers):
        return sum(model.node_colors[node, color] for color in model.colors) == 1

    model.one_color = pe.Constraint(model.nodes, rule=one_color)

    def color_assignment_one(model, color: pe.NonNegativeIntegers):
        return model.color_used[color] <= sum(model.node_colors[n, color] for n in model.nodes)

    model.color_assignment_one = pe.Constraint(model.colors, rule=color_assignment_one)

    def color_assignment_two(model, color: pe.NonNegativeIntegers):
        if color == 0:
            return pe.Constraint.Skip
        else:
            return model.color_used[color] <= model.color_used[color - 1]

    model.color_assignment_two = pe.Constraint(model.colors, rule=color_assignment_two)

    def color_assignment_three(model):
        return model.node_colors[0, 0] == 1

    model.color_assignment_three = pe.Constraint(rule=color_assignment_three)

    solver = pe.SolverFactory("gurobi")
    solver.options["TimeLimit"] = 300
    solver.solve(model, tee=True) # options="TimeLimit=60",

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


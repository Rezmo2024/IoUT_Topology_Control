import pulp
# Define the graph as a dictionary of dictionaries
Cost_Graph = {
    'A': {'B': 4, 'C': 1, 'D': 2},
    'B': {'C': 2, 'E': 1,'A': 4},
    'C': {'D': 3, 'F': 2, 'A': 1,'B': 2},
    'D': {'G': 7, 'A': 2,'C': 3},
    'E': {'H': 3, 'F': 7, 'B': 1},
    'H': {'F': 5, 'E': 3, 'G': 4},
    'F': {'H': 5, 'G': 2,'C': 2, 'E': 7},
    'G': {'H': 4, 'D': 7, 'F': 2 },
}
Delay_Graph = {
    'A': {'B': 40, 'C': 10, 'D': 20},
    'B': {'C': 20, 'E': 10,'A': 40},
    'C': {'D': 30, 'F': 20, 'A': 10,'B': 20},
    'D': {'G': 70, 'A': 20,'C': 30},
    'E': {'H': 30, 'F': 70, 'B': 10},
    'H': {'F': 15, 'E': 30, 'G': 40},
    'F': {'H': 15, 'G': 20,'C': 20, 'E': 70},
    'G': {'H': 40, 'D': 70, 'F': 20 },
}
# Define the source and Destination nodes
source = 'G'
Destination = 'B'
def CalculatePath(source,Destination,first_graph,second_graph,alpha):
    # Create a PuLP model
    model = pulp.LpProblem('Weighted_Multiobjetive', pulp.LpMinimize)
    # Define the decision variables
    variables = {}
    for node in first_graph:
        for neighbor in first_graph[node]:
            variables[f'x_{node}_{neighbor}'] = pulp.LpVariable(f'x_{node}_{neighbor}', cat='Binary')
    # Define the objective function
    w1=alpha
    w2=1-w1
    first_objective=w1*sum(first_graph[node][neighbor] * variables[f'x_{node}_{neighbor}'] for node in first_graph for neighbor in first_graph[node] )
    second_objective=w2*sum(second_graph[node][neighbor] * variables[f'x_{node}_{neighbor}'] for node in second_graph for neighbor in second_graph[node] )
    model +=first_objective+second_objective
    # Define Constraints
   
    model +=((sum( variables[f'x_{node}_{neighbor}'] for node in first_graph for neighbor in first_graph[node] if node==source)-sum( variables[f'x_{neighbor}_{node}'] for neighbor in first_graph for node in first_graph[neighbor] if node==source))==1,"Source Constarint")
    for node in first_graph:
        if node != source and node!=Destination:
            model += ((sum(variables[f'x_{prev_node}_{node}'] for prev_node in first_graph if node in first_graph[prev_node]) - sum(variables[f'x_{node}_{next_node}'] for next_node in first_graph[node] ))==0,"Intermediate Nodes Constraint_"+str(node))
            
    model +=((sum( variables[f'x_{node}_{neighbor}'] for node in first_graph for neighbor in first_graph[node] if node==Destination)-sum( variables[f'x_{neighbor}_{node}'] for neighbor in first_graph for node in first_graph[neighbor] if node==Destination))==-1,"Destination Constraint")
    #print(model)
    # Solve the model
    model.solve(pulp.PULP_CBC_CMD(msg=0))
    #print(model.variables)
    if pulp.LpStatusOptimal ==1: #optimal
        #print(f'Status: {pulp.LpStatus[model.status]}')
        path=[]
        for node in first_graph:
            for neighbor in first_graph[node]:
                    if variables[f'x_{node}_{neighbor}'].varValue == 1:
                        #print(f'({node}, {neighbor})',end="")
                        path.append((node,neighbor))
        #print("\n Optimal Cost(W1="+str("{:.3f}".format(w1))+", W2="+str("{:.3f}".format(w2))+")=", pulp.value(model.objective))
        p=[]
        p.append(source)
        ind=0
        c=0
        while True:
            for item in path:
                if item[0]==p[ind]:
                    p.append(item[1])
                    ind+=1
                    c=c+1
            if c==len(path):
                break 
        return p
    else:
        return None

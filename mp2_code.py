class Relation:
    def __init__(self, name, tuples, attributes, distinct_vals = []):
        self.name = name
        self.tuples = tuples
        self.attributes = attributes
        self.distinct_vals = distinct_vals
    def get_name(self):
        return self.name
    def get_tuples(self):
        return self.tuples
    def set_tuples(self, val):
        self.tuples = val
    def get_attributes(self):
        return self.attributes
    def set_attributes(self, attributes):
        self.attributes = attributes
    def set_distinct_vals(self, val):
        self.distinct_vals = val
    def get_distinct_vals(self):
        return self.distinct_vals
    def __str__(self):
        return f"Name: {self.name}\nTuples: {self.tuples}\n"#Attributes: {self.attributes}\nDistinct Values: {self.distinct_vals}"


def get_table_from_name(table_name, tables):
    
    for table in tables:
        if(table.get_name() == table_name):
            return table
 
def resolve_selectivity(selectivity):
    if(len(selectivity) == 1):
        return selectivity[0]
    
    total_selectivity = selectivity[0]
    start = 1
    if(total_selectivity == '~'):
        total_selectivity = 1 - selectivity[1]
        start = 2
    for i in range(start, len(selectivity)):
        if(selectivity[i] == 'and'):
            if selectivity[i+1] == '~':
               
                total_selectivity *=  (1 - selectivity[i+2])
            else:
                total_selectivity *=  selectivity[i+1]
        elif(selectivity[i] == 'or'):
            if selectivity[i+1] == '~':
                total_selectivity +=  (1 - selectivity[i+2])
            else:
                total_selectivity += selectivity[i+1]
        
            
    return total_selectivity
 
def solve_predicate(predicate, res_table):

    i = 0
    #print(predicate)
    while(i < len(predicate)-1):
        if(predicate[i] == '!' and predicate[i+1] == '='):
            predicate = predicate[:i] + " != " + predicate[i+2: ]
            i += 4
        elif(predicate[i] == '='):
            predicate = predicate[:i] + " = " + predicate[i+1: ]
            i += 3
        else:
            i += 1
    
    predicate = predicate.replace('<', ' < ')
    predicate = predicate.replace('>', ' > ')
    #predicate = predicate.replace('~', ' ~ ')
    #predicate = predicate.replace('or', ' or ')
    #predicate = predicate.replace('and', ' and ')
    tokens = predicate.split(" ")
    
    selectivity = []
    i = 0

    #print(tokens)
    while(i < len(tokens)):
        
        if tokens[i] == '=':     
            left = tokens[i-1]
            right = int(tokens[i+1])
            if(left[-1] not in res_table.get_attributes()):
                selectivity += [1]
                i += 1
                continue
            ind = res_table.get_attributes().index(left[-1])
            range_stats = input(f"Do you wish to provide range statistics for {left} ")
            
            if range_stats in 'yY1':
                j = 0
                ranges = []
                choice = "1"                
                while(choice in "1yY" and j <  res_table.get_distinct_vals()[res_table.get_attributes().index(left)]):
                    start_of_range = int(input("Enter start of range "))
                    end_of_range = int(input("Enter end of range "))
                    number_of_tuples = int(input("Enter tuples in this range "))
                    ranges.append([[start_of_range, end_of_range], number_of_tuples])
                    j +=1
                    choice = input("Add more?...")
                    
                diff = 0
                t = 0
                for k in ranges:
                    if(right <= k[0][1] and right >= k[0][0]):
                        diff = k[0][1] - k[0][0] + 1
                        t = k[1]
                        break
                
                selectivity += [(t/res_table.get_tuples()) * (1/diff)] 
            else:
                selectivity += [1/res_table.get_distinct_vals()[ind]]   #T(R)/V(R, Y)
                
        elif tokens[i] == '!=':
            left = tokens[i-1]

            if(left[-1] not in res_table.get_attributes()):
                selectivity += [1]
                i += 1
                continue
            ind = res_table.get_attributes().index(left[-1])
            v = res_table.get_distinct_vals()[ind]
            selectivity += [((v-1)/v)]
            i += 1
        elif tokens[i] == '<':
            left = tokens[i-1]
            right = int(tokens[i+1])

            if(left[-1] not in res_table.get_attributes()):
                selectivity += [1]
                i += 1
                continue
            
            range_stats = input(f"Do you wish to provide a uniform range for {left} ")
            
            if range_stats in 'yY1':
                j = 0
            
                choice = "1"                
                
                start_of_range = int(input("Enter start of range "))
                end_of_range = int(input("Enter end of range "))

                if(end_of_range < right):
                    selectivity += [1]
                elif(start_of_range > right):
                    selectivity += [0]
                else:
                    selectivity += [(right - start_of_range)/((end_of_range - start_of_range) + 1)]
                
            else:
                selectivity += [1/3]
                
        elif tokens[i] == '>':
            left = tokens[i-1]
            right = int(tokens[i+1])

            if(left[-1] not in res_table.get_attributes()):
                selectivity += [1]
                i += 1
                continue
            
            range_stats = input(f"Do you wish to provide a uniform range for {left} ")
            
            if range_stats in 'yY1':
                j = 0
            
                choice = "1"                
                
                start_of_range = int(input("Enter start of range "))
                end_of_range = int(input("Enter end of range "))

                if(end_of_range < right):
                    selectivity += [0]
                elif(start_of_range > right):
                    selectivity += [1]
                else:
                    selectivity += [(end_of_range - right)/((end_of_range - start_of_range) + 1)]
            else:
                selectivity += [1/3]
            
            
        elif tokens[i] == 'and' or tokens[i] == 'or' or tokens[i] == '~':
            selectivity += [tokens[i]]
                 
        i += 1
    print("Selectivity metrics: " , selectivity)
    selectivity = resolve_selectivity(selectivity)
    print(selectivity)
    return(selectivity * res_table.get_tuples())
        
   
def find_common_attribute(t1, t2):
    for i in t1.get_attributes():
        for j in t2.get_attributes():
            if i[-1] == j[-1]:
                return [t1.get_distinct_vals()[t1.get_attributes().index(i)], t2.get_distinct_vals()[t2.get_attributes().index(j)]]
    print("No common attributes...Something fishy")
    return None
def apply(stack_top, res_table, prefix, tables):

    
    if(stack_top[0] == ','):
        return res_table
    print("Trying to resolve: ")
    print(stack_top)
  
    if(stack_top[0] not in 'PSJC' and stack_top[0] != ',' and stack_top != 'J[]'):
        table = get_table_from_name(stack_top[0], tables)
        
        res_table.set_tuples(table.get_tuples())
        res_table.set_attributes(table.get_attributes())
        res_table.set_distinct_vals(table.get_distinct_vals())
        prefix += [table]
    
    
    elif(stack_top[0] == "P"):
        #table = get_table_from_name(stack_top[0], tables)
        
        attrs = stack_top[2:len(stack_top)-1].strip().split(",")
        res_table.set_attributes(attrs)
        
        dist_vals = []
        for i in attrs:
            ind = res_table.get_attributes().index(i)
            
            dist_vals += [res_table.get_distinct_vals()[ind]]
        res_table.set_distinct_vals(dist_vals)
        
        prefix += [res_table]

    elif stack_top == 'J[]':
        print("here")
        first_table, second_table = prefix[-1], prefix[-2]
        
        dv1, dv2 = find_common_attribute(first_table, second_table)
        
        t = (first_table.get_tuples() * second_table.get_tuples())/(max(dv1, dv2))
        res_table.set_tuples(t)
        res_table.set_attributes(first_table.get_attributes() + second_table.get_attributes())
        res_table.set_distinct_vals(first_table.get_distinct_vals() + second_table.get_distinct_vals())
        
        prefix += [res_table]
       
    
    elif stack_top[0] == 'S' and "J" not in stack_top:
        predicate = stack_top[2:len(stack_top)-1].strip()
        prefix += [res_table]
        res_table.set_tuples(solve_predicate(predicate, res_table))
        
        
    elif stack_top[0] == 'S':
        first_table, second_table = prefix[-1], prefix[-2]
        ind = stack_top.index("]")+1
        
        res_table1 = apply(stack_top[:ind], first_table, prefix, tables)
        res_table2 = apply(stack_top[:ind], second_table, prefix, tables)
        
        dv1, dv2 = find_common_attribute(first_table, second_table)
        
        t = (res_table1.get_tuples() * res_table2.get_tuples())/(max(dv1, dv2))
        res_table.set_tuples(t)
        res_table.set_attributes(first_table.get_attributes() + second_table.get_attributes())
        res_table.set_distinct_vals(first_table.get_distinct_vals() + second_table.get_distinct_vals())
        
        prefix += [res_table]
    elif stack_top == 'C':
        first_table, second_table = prefix[-1], prefix[-2]
        res_table.set_tuples(first_table.get_tuples() * second_table.get_tuples())
        res_table.set_attributes(first_table.get_attributes() + second_table.get_attributes())
        res_table.set_distinct_vals(first_table.get_distinct_vals() + second_table.get_distinct_vals())
        prefix += [res_table]
    print("Relation till Now seems to be: ")
    print(prefix[-1]) 
    print()
    return res_table
        

def get_params(i, expression):
    opening = expression[i+1:].find("[")
    closing = expression[i+1:].find("]")
    return [i + opening+1, i + closing + 1]

def get_params_for_s(i, expression):
    opening = expression[i+1:].find("[")
    closing = expression[i+1:].find("]")
    if(i + closing + 3 < len(expression) and expression[i +closing+2: i + closing+4] == ',J'):
        
        closing += 1 + expression[i + closing+2:].find(']')
        
    print(i + closing + 1)
    return [i + opening+1, i + closing + 1]
    
    
def parse_expression(expression, tables):
    expression = "(" + expression + ")"
       
    res = Relation("Result", 0, 0)
    
    stack = []
    
    prefix = []
    n = len(expression)
    i = 0
    while(i < n):
        #print (stack)
        
        if(expression[i] == '('):
            stack.append("(")
        elif (expression[i] in 'S'):
            
            opening, closing = get_params_for_s(i, expression)
            
            stack.append(expression[i] + expression[opening: closing + 1])
            expression = expression[: opening] + expression[closing+1: ]
        elif (expression[i] in 'PJ'):
            opening, closing = get_params(i, expression)
            stack.append(expression[i] + expression[opening: closing + 1])
            expression = expression[: opening] + expression[closing+1: ]
        
        elif expression[i] == ')':
            while(stack != [] and stack[-1] != "("):
        
                res = apply(stack[-1], res, prefix, tables)
                stack.pop()
            if(stack != []):
                stack.pop()
        else:
            stack.append(expression[i])
        #print(stack)
        i += 1
        n = len(expression)
    print("Total number of tuples = " + str(res.get_tuples()))
    print("Rounded result = " + str(round(res.get_tuples())))
        

def get_relations(query):
    relations = set()
    for i in query:
        if i.isupper() and i.isalpha() and i not in "PSJC":
            relations.add(i)
    return relations

def get_parameters(relations):
    tables = []
    for table in relations:
        name = table

        attributes = input(f"Enter the attributes for relation {table}: ")
        disinct_vals = input(f"Enter the distinct values of attributes for relation {table}: ")
        num_tuples = int(input(f"Enter the number of tuples in relation {table}: "))
        
        dv = [int(i) for i in disinct_vals.split(" ")]
        relation = Relation(name, num_tuples, attributes.split(" "), dv)
        tables.append(relation)
    
    return tables

def main():
    
    #expression = "S([a>10],R)"
    #expression = "S([~ a=10],R)"
    #expression = "S([a=10 and b<10 and c<3],R)"
    #expression = "P([a,T.c],S([a<5],J([](R,T))))"
    #expression = "P([a,c],S([a=5 and b=10],J([](R,T))))"
    #expression = "S([~ c>30 and d>40],C(R,T))"
    #expression = "P([a,b],J([](R,T)))"
    
    expression = input("Enter the relational query: ")
    
    relations = list(get_relations(expression))
    tables = get_parameters(relations)

    
    parse_expression(expression, tables)


if __name__ == "__main__":
    main()
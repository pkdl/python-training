#!/usr/bin/python

class Scope(object):
    def __init__(self, parent = None):
        self.data = {}
        self.parent = parent

    def __setitem__(self, key, item):
        self.data[key] = item

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        elif self.parent:
            return self.parent[key]

class Number:
    def __init__(self, value):
        self.value = value
    def evaluate(self, scope):
        return self

class Conditional:
    def __init__(self, condtion, if_true, if_false = None):
        self.condtion = condtion
        self.if_true = if_true
        self.if_false = if_false
    def evaluate(self, scope):
        if self.condtion.evaluate(scope).value == 0:
            body = self.if_false
        else:
            body = self.if_true

        result = Number(0)
        for obj in body or []:
            result = obj.evaluate(scope)

        return result

class Print:
    def __init__(self, expr):
        self.expr = expr
    def evaluate(self, scope):
        result = self.expr.evaluate(scope)
        print(result.value)
        return result

class Read:
    def __init__(self, name):
        self.name = name
    def evaluate(self, scope):
        result = Number(int(input()))
        scope[self.name] = result
        return result

class FunctionCall:
    def __init__(self, fun_expr, args):
        self.fun_expr = fun_expr
        self.args = args
    def evaluate(self, scope):
        function = self.fun_expr.evaluate(scope)
        call_scope = Scope(scope)
        for obj, name in zip(self.args, function.args):
            call_scope[name] = obj.evaluate(scope)
        return function.evaluate(call_scope)

class Function:
    def __init__(self, args, body):
        self.body = body
        self.args = args
    def evaluate(self, scope):
        result = Number(0)
        for obj in self.body:
            result = obj.evaluate(scope)
        return result

class FunctionDefinition:
    def __init__(self, name, function):
        self.name = name
        self.function = function
    def evaluate(self, scope):
        scope[self.name] = self.function
        return self.function
        
class Reference:
    def __init__(self, name):
        self.name = name
    def evaluate(self, scope):
        return scope[self.name]

class BinaryOperation:
    command = {
        '+' : lambda lhs, rhs: lhs.value + rhs.value,
        '-' : lambda lhs, rhs: lhs.value - rhs.value,
        '*' : lambda lhs, rhs: lhs.value * rhs.value,
        '/' : lambda lhs, rhs: lhs.value // rhs.value,
        '%' : lambda lhs, rhs: lhs.value % rhs.value,
        '==': lambda lhs, rhs: 1 if lhs.value == rhs.value else 0,
        '!=': lambda lhs, rhs: 1 if lhs.value != rhs.value else 0,
        '>' : lambda lhs, rhs: 1 if lhs.value > rhs.value else 0,
        '<' : lambda lhs, rhs: 1 if lhs.value < rhs.value else 0,
        '>=': lambda lhs, rhs: 1 if lhs.value >= rhs.value else 0,
        '<=': lambda lhs, rhs: 1 if lhs.value <= rhs.value else 0,
        '&&': lambda lhs, rhs: lhs.value and rhs.value,
        '||': lambda lhs, rhs: lhs.value or rhs.value
    }

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
    def evaluate(self, scope):
        lhs = self.lhs.evaluate(scope)
        rhs = self.rhs.evaluate(scope)

        return Number(self.command[self.op](lhs, rhs))

class UnaryOperation:
    command = {
        '!': lambda expr: 1 if expr == Number(0) else 0,
        '-': lambda expr: -expr.value
    }

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def evaluate(self, scope):
        expr = self.expr.evaluate(scope)

        return Number(self.command[self.op](expr))        

def test():
    print("### Scope tests:")
    
    parent = Scope()
    
    parent["foo"] = "foo in parent"
    print(parent["foo"])
    
    scope = Scope(parent)
    scope["bar"] = "bar in scope"
    print(scope["bar"])
    print(scope["foo"])

    print("### Number tests:")
    scope["num"] = Number(17)
    print(scope["num"].value)

    print("### Print tests:")
    a = Print(scope["num"])
    a.evaluate(scope)

    b = Print(BinaryOperation(Number(15), '||', Number(0)))
    b.evaluate(scope)


    print("###Functions tests")
    func = Function(["x", "y"], [BinaryOperation(Reference("x"), "+", Reference("y"))])
    definition = FunctionDefinition("sum", func)
    call = FunctionCall(definition, [Number(2), Number(3)])
    pr = Print(call)
    pr.evaluate(scope)

    func = Function([], [])
    definition = FunctionDefinition("sum", func)
    call = FunctionCall(definition, [])
    pr = Print(call)
    pr.evaluate(scope)


    print("###Conditional tests")
    cond = Conditional(BinaryOperation(Number(5), ">", Number(7)), None, [Print(Number(19))])
    cond.evaluate(scope)
    cond1 = Conditional(BinaryOperation(Number(5), "&&", Number(7)), None, [])
    cond1.evaluate(scope)


def example():
    parent = Scope()
    parent["foo"] = Function(('hello', 'world'),
                             [Print(BinaryOperation(Reference('hello'),
                                                    '+',
                                                    Reference('world')))])
    parent["bar"] = Number(10)
    scope = Scope(parent)
    assert 10 == scope["bar"].value
    scope["bar"] = Number(20)
    assert scope["bar"].value == 20
    print('It should print 2: ', end=' ')
    FunctionCall(FunctionDefinition('foo', parent['foo']),
                 [Number(5), UnaryOperation('-', Number(3))]).evaluate(scope)



if __name__ == "__main__":
    test()
    example()
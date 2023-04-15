class Modification:
    def __init__(self, name, params):
        self.operation_name = name
        self.params = [] # {key / value}
        self.params.extend(params)

    def describe(self):
        string = "{} with parameters : ".format(self.operation_name)
        for i, param in enumerate(self.params):
            string += "{} {}".format(param['key'] , param['value'])
            if i < len(self.params) - 1:
                string += " , "
        return string

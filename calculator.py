class Calculator:
    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y

    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        if y == 0:
            return "Cannot divide by zero"
        return x / y

# 创建计算器实例
calc = Calculator()

# 进行一些计算
result_add = calc.add(5, 3)
result_subtract = calc.subtract(10, 4)
result_multiply = calc.multiply(6, 7)
result_divide = calc.divide(20, 5)
result_divide_by_zero = calc.divide(5, 0)

# 打印结果
print(f"Addition: 5 + 3 = {result_add}")
print(f"Subtraction: 10 - 4 = {result_subtract}")
print(f"Multiplication: 6 * 7 = {result_multiply}")
print(f"Division: 20 / 5 = {result_divide}")
print(f"Division by zero: 5 / 0 = {result_divide_by_zero}") 
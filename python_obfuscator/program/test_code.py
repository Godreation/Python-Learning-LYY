# 测试代码

def calculate_sum(a, b):
    """计算两个数的和"""
    result = a + b
    return result

def fibonacci(n):
    """计算斐波那契数列的第n项"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# 测试变量
x = 10
y = 20

# 测试控制流
if x > y:
    print(f"{x} 大于 {y}")
else:
    print(f"{x} 小于或等于 {y}")

# 测试循环
for i in range(5):
    print(f"循环次数: {i}")

# 测试函数调用
sum_result = calculate_sum(x, y)
print(f"和为: {sum_result}")

fib_result = fibonacci(10)
print(f"斐波那契数列第10项: {fib_result}")

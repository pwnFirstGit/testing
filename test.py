def factorial(n):
    if n == 0:
        return 1  
    return n * factorial(n - 1)

try:
    num = 5
    print(f"Factorial of {num} is: {factorial(num)}")
except RecursionError as e:
    print("RecursionError:", e)
except Exception as e:
    print(f"Error: {e}")
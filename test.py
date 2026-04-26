def factorial(n):
    
    if n == 0:  
        return 0  

    return n * factorial(n - 1)


# Test the faulty function
try:
    num = 5
    print(f"Factorial of {num} is: {factorial(num)}")
except RecursionError:
    print("RecursionError: Infinite recursion detected!")
except Exception as e:
    print(f"Error: {e}")

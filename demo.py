"""
Demo Python Module for CodeDoc AI 🚀

This module contains sample functions and classes to demonstrate
the power of CodeDoc AI documentation generation.
"""

import math
from typing import List, Optional


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the discount amount for a given price and percentage.
    
    Args:
        price: The original price
        discount_percent: Discount percentage (0-100)
        
    Returns:
        The discount amount
    """
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percentage must be between 0 and 100")
    
    return price * (discount_percent / 100)


def fibonacci_sequence(n: int) -> List[int]:
    """Generate Fibonacci sequence up to n numbers."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib


async def fetch_user_data(user_id: str) -> Optional[dict]:
    """Async function to fetch user data from API.
    
    Args:
        user_id: The user ID to fetch
        
    Returns:
        User data dictionary or None if not found
    """
    # Simulate API call
    await asyncio.sleep(0.1)
    return {"id": user_id, "name": "Sample User"}


class Calculator:
    """A simple calculator class with basic mathematical operations."""
    
    def __init__(self, precision: int = 2):
        """Initialize calculator with specified precision."""
        self.precision = precision
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = round(a + b, self.precision)
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract second number from first."""
        result = round(a - b, self.precision)
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = round(a * b, self.precision)
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """Divide first number by second."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = round(a / b, self.precision)
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()


class DataProcessor(Calculator):
    """Advanced data processor with statistical operations."""
    
    def __init__(self, precision: int = 2):
        """Initialize data processor."""
        super().__init__(precision)
        self.data_store = {}
    
    def calculate_mean(self, numbers: List[float]) -> float:
        """Calculate arithmetic mean of numbers."""
        if not numbers:
            raise ValueError("Cannot calculate mean of empty list")
        return sum(numbers) / len(numbers)
    
    def calculate_median(self, numbers: List[float]) -> float:
        """Calculate median of numbers."""
        if not numbers:
            raise ValueError("Cannot calculate median of empty list")
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        if n % 2 == 0:
            return (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
        return sorted_nums[n//2]
    
    def store_data(self, key: str, value: any) -> None:
        """Store data with a key."""
        self.data_store[key] = value
    
    def retrieve_data(self, key: str) -> any:
        """Retrieve stored data by key."""
        return self.data_store.get(key)


if __name__ == "__main__":
    # Demo usage
    calc = Calculator()
    result = calc.add(10, 5)
    print(f"10 + 5 = {result}")
    
    processor = DataProcessor()
    mean = processor.calculate_mean([1, 2, 3, 4, 5])
    print(f"Mean of [1,2,3,4,5] = {mean}") 
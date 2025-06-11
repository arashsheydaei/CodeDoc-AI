# 🚀 CodeDoc AI Documentation

Generated on 2025-06-12 00:51:30

📊 **Statistics:** 13 Functions, 2 Classes

---

## 📋 Functions

### calculate_discount

**Description:** Calculate the discount amount for a given price and percentage.

Args:
    price: The original price
    discount_percent: Discount percentage (0-100)
    
Returns:
    The discount amount

**Parameters:** price, discount_percent

<details>
<summary>📄 Source Code</summary>

```python


def calculate_discount(price: float, discount_percent: float) -> float:
    'Calculate the discount amount for a given price and percentage.\n    \n    Args:\n        price: The original price\n        discount_percent: Discount percentage (0-100)\n        \n    Returns:\n        The discount amount\n    '
    if ((discount_percent < 0) or (discount_percent > 100)):
        raise ValueError('Discount percentage must be between 0 and 100')
    return (price * (discount_percent / 100))

```

</details>

---

### fibonacci_sequence

**Description:** Generate Fibonacci sequence up to n numbers.

**Parameters:** n

<details>
<summary>📄 Source Code</summary>

```python


def fibonacci_sequence(n: int) -> List[int]:
    'Generate Fibonacci sequence up to n numbers.'
    if (n <= 0):
        return []
    elif (n == 1):
        return [0]
    elif (n == 2):
        return [0, 1]
    fib = [0, 1]
    for i in range(2, n):
        fib.append((fib[(i - 1)] + fib[(i - 2)]))
    return fib

```

</details>

---

### __init__

**Description:** Initialize calculator with specified precision.

**Parameters:** self, precision

<details>
<summary>📄 Source Code</summary>

```python


def __init__(self, precision: int=2):
    'Initialize calculator with specified precision.'
    self.precision = precision
    self.history = []

```

</details>

---

### add

**Description:** Add two numbers.

**Parameters:** self, a, b

<details>
<summary>📄 Source Code</summary>

```python


def add(self, a: float, b: float) -> float:
    'Add two numbers.'
    result = round((a + b), self.precision)
    self.history.append(f'{a} + {b} = {result}')
    return result

```

</details>

---

### multiply

**Description:** Multiply two numbers.

**Parameters:** self, a, b

<details>
<summary>📄 Source Code</summary>

```python


def multiply(self, a: float, b: float) -> float:
    'Multiply two numbers.'
    result = round((a * b), self.precision)
    self.history.append(f'{a} × {b} = {result}')
    return result

```

</details>

---

### power

**Description:** Calculate base raised to the power of exponent.

**Parameters:** self, base, exponent

<details>
<summary>📄 Source Code</summary>

```python


def power(self, base: float, exponent: float) -> float:
    'Calculate base raised to the power of exponent.'
    result = round(math.pow(base, exponent), self.precision)
    self.history.append(f'{base}^{exponent} = {result}')
    return result

```

</details>

---

### get_history

**Description:** Get calculation history.

**Parameters:** self

<details>
<summary>📄 Source Code</summary>

```python


def get_history(self) -> List[str]:
    'Get calculation history.'
    return self.history.copy()

```

</details>

---

### clear_history

**Description:** Clear calculation history.

**Parameters:** self

<details>
<summary>📄 Source Code</summary>

```python


def clear_history(self) -> None:
    'Clear calculation history.'
    self.history.clear()

```

</details>

---

### __init__

**Parameters:** self

<details>
<summary>📄 Source Code</summary>

```python


def __init__(self):
    self.data = []

```

</details>

---

### add_data

**Description:** Add new data points.

**Parameters:** self, values

<details>
<summary>📄 Source Code</summary>

```python


def add_data(self, values: List[float]) -> None:
    'Add new data points.'
    self.data.extend(values)

```

</details>

---

### calculate_mean

**Description:** Calculate the arithmetic mean of the data.

**Parameters:** self

<details>
<summary>📄 Source Code</summary>

```python


def calculate_mean(self) -> Optional[float]:
    'Calculate the arithmetic mean of the data.'
    if (not self.data):
        return None
    return (sum(self.data) / len(self.data))

```

</details>

---

### calculate_median

**Description:** Calculate the median of the data.

**Parameters:** self

<details>
<summary>📄 Source Code</summary>

```python


def calculate_median(self) -> Optional[float]:
    'Calculate the median of the data.'
    if (not self.data):
        return None
    sorted_data = sorted(self.data)
    n = len(sorted_data)
    if ((n % 2) == 0):
        return ((sorted_data[((n // 2) - 1)] + sorted_data[(n // 2)]) / 2)
    else:
        return sorted_data[(n // 2)]

```

</details>

---

### get_summary

**Description:** Get a summary of the data statistics.

**Parameters:** self

<details>
<summary>📄 Source Code</summary>

```python


def get_summary(self) -> dict:
    'Get a summary of the data statistics.'
    if (not self.data):
        return {'error': 'No data available'}
    return {'count': len(self.data), 'mean': self.calculate_mean(), 'median': self.calculate_median(), 'min': min(self.data), 'max': max(self.data), 'range': (max(self.data) - min(self.data))}

```

</details>

---

## 🏗️ Classes

### Calculator

**Description:** A simple calculator class with basic mathematical operations.

**🔧 Methods:**
- **__init__**(self, precision) - Initialize calculator with specified precision.
- **add**(self, a, b) - Add two numbers.
- **multiply**(self, a, b) - Multiply two numbers.
- **power**(self, base, exponent) - Calculate base raised to the power of exponent.
- **get_history**(self) - Get calculation history.
- **clear_history**(self) - Clear calculation history.

<details>
<summary>📄 Source Code</summary>

```python


class Calculator():
    'A simple calculator class with basic mathematical operations.'

    def __init__(self, precision: int=2):
        'Initialize calculator with specified precision.'
        self.precision = precision
        self.history = []

    def add(self, a: float, b: float) -> float:
        'Add two numbers.'
        result = round((a + b), self.precision)
        self.history.append(f'{a} + {b} = {result}')
        return result

    def multiply(self, a: float, b: float) -> float:
        'Multiply two numbers.'
        result = round((a * b), self.precision)
        self.history.append(f'{a} × {b} = {result}')
        return result

    def power(self, base: float, exponent: float) -> float:
        'Calculate base raised to the power of exponent.'
        result = round(math.pow(base, exponent), self.precision)
        self.history.append(f'{base}^{exponent} = {result}')
        return result

    def get_history(self) -> List[str]:
        'Get calculation history.'
        return self.history.copy()

    def clear_history(self) -> None:
        'Clear calculation history.'
        self.history.clear()

```

</details>

---

### DataProcessor

**Description:** Process and analyze data with various statistical operations.

**🔧 Methods:**
- **__init__**(self)
- **add_data**(self, values) - Add new data points.
- **calculate_mean**(self) - Calculate the arithmetic mean of the data.
- **calculate_median**(self) - Calculate the median of the data.
- **get_summary**(self) - Get a summary of the data statistics.

<details>
<summary>📄 Source Code</summary>

```python


class DataProcessor():
    'Process and analyze data with various statistical operations.'

    def __init__(self):
        self.data = []

    def add_data(self, values: List[float]) -> None:
        'Add new data points.'
        self.data.extend(values)

    def calculate_mean(self) -> Optional[float]:
        'Calculate the arithmetic mean of the data.'
        if (not self.data):
            return None
        return (sum(self.data) / len(self.data))

    def calculate_median(self) -> Optional[float]:
        'Calculate the median of the data.'
        if (not self.data):
            return None
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        if ((n % 2) == 0):
            return ((sorted_data[((n // 2) - 1)] + sorted_data[(n // 2)]) / 2)
        else:
            return sorted_data[(n // 2)]

    def get_summary(self) -> dict:
        'Get a summary of the data statistics.'
        if (not self.data):
            return {'error': 'No data available'}
        return {'count': len(self.data), 'mean': self.calculate_mean(), 'median': self.calculate_median(), 'min': min(self.data), 'max': max(self.data), 'range': (max(self.data) - min(self.data))}

```

</details>

---


---
*Generated by **🚀 CodeDoc AI** - The future of code documentation!*
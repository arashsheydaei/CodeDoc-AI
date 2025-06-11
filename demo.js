/**
 * Demo JavaScript Module for CodeDoc AI 🚀
 * 
 * This module contains sample functions and classes to demonstrate
 * the power of CodeDoc AI documentation generation for JavaScript.
 */

/**
 * Calculate the discount amount for a given price and percentage
 * @param {number} price - The original price
 * @param {number} discountPercent - Discount percentage (0-100)
 * @returns {number} The discount amount
 * @throws {Error} If discount percentage is invalid
 */
function calculateDiscount(price, discountPercent) {
    if (discountPercent < 0 || discountPercent > 100) {
        throw new Error("Discount percentage must be between 0 and 100");
    }
    
    return price * (discountPercent / 100);
}

/**
 * Generate Fibonacci sequence up to n numbers
 * @param {number} n - Number of Fibonacci numbers to generate
 * @returns {number[]} Array of Fibonacci numbers
 */
const fibonacciSequence = (n) => {
    if (n <= 0) return [];
    if (n === 1) return [0];
    if (n === 2) return [0, 1];
    
    const fib = [0, 1];
    for (let i = 2; i < n; i++) {
        fib.push(fib[i-1] + fib[i-2]);
    }
    
    return fib;
};

/**
 * Async function to fetch user data from API
 * @param {string} userId - The user ID to fetch
 * @returns {Promise<Object>} User data object
 */
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch user data:', error);
        throw error;
    }
}

/**
 * A simple calculator class with basic mathematical operations
 */
class Calculator {
    /**
     * Initialize calculator with specified precision
     * @param {number} precision - Number of decimal places for results
     */
    constructor(precision = 2) {
        this.precision = precision;
        this.history = [];
    }
    
    /**
     * Add two numbers
     * @param {number} a - First number
     * @param {number} b - Second number
     * @returns {number} Sum of a and b
     */
    add(a, b) {
        const result = this._roundResult(a + b);
        this.history.push(`${a} + ${b} = ${result}`);
        return result;
    }
    
    /**
     * Subtract second number from first
     * @param {number} a - First number
     * @param {number} b - Second number
     * @returns {number} Difference of a and b
     */
    subtract(a, b) {
        const result = this._roundResult(a - b);
        this.history.push(`${a} - ${b} = ${result}`);
        return result;
    }
    
    /**
     * Multiply two numbers
     * @param {number} a - First number
     * @param {number} b - Second number
     * @returns {number} Product of a and b
     */
    multiply(a, b) {
        const result = this._roundResult(a * b);
        this.history.push(`${a} * ${b} = ${result}`);
        return result;
    }
    
    /**
     * Divide first number by second
     * @param {number} a - Dividend
     * @param {number} b - Divisor
     * @returns {number} Quotient of a and b
     * @throws {Error} If dividing by zero
     */
    divide(a, b) {
        if (b === 0) {
            throw new Error("Cannot divide by zero");
        }
        const result = this._roundResult(a / b);
        this.history.push(`${a} / ${b} = ${result}`);
        return result;
    }
    
    /**
     * Get calculation history
     * @returns {string[]} Array of calculation history strings
     */
    getHistory() {
        return [...this.history];
    }
    
    /**
     * Clear calculation history
     */
    clearHistory() {
        this.history = [];
    }
    
    /**
     * Private method to round results to specified precision
     * @param {number} value - Value to round
     * @returns {number} Rounded value
     * @private
     */
    _roundResult(value) {
        return Math.round(value * Math.pow(10, this.precision)) / Math.pow(10, this.precision);
    }
}

/**
 * Modern ES6 class with advanced features
 */
class DataProcessor extends Calculator {
    /**
     * Initialize data processor
     * @param {Object} options - Configuration options
     * @param {number} options.precision - Decimal precision
     * @param {boolean} options.logging - Enable logging
     */
    constructor(options = {}) {
        super(options.precision);
        this.logging = options.logging || false;
        this.data = new Map();
    }
    
    /**
     * Process array of numbers with a given operation
     * @param {number[]} numbers - Array of numbers to process
     * @param {string} operation - Operation to perform ('sum', 'average', 'max', 'min')
     * @returns {number} Processed result
     */
    processArray(numbers, operation) {
        if (!Array.isArray(numbers) || numbers.length === 0) {
            throw new Error("Invalid input: expected non-empty array");
        }
        
        let result;
        switch (operation) {
            case 'sum':
                result = numbers.reduce((sum, num) => sum + num, 0);
                break;
            case 'average':
                result = numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
                break;
            case 'max':
                result = Math.max(...numbers);
                break;
            case 'min':
                result = Math.min(...numbers);
                break;
            default:
                throw new Error(`Unsupported operation: ${operation}`);
        }
        
        result = this._roundResult(result);
        
        if (this.logging) {
            console.log(`${operation}(${numbers.join(', ')}) = ${result}`);
        }
        
        return result;
    }
    
    /**
     * Store data with a key
     * @param {string} key - Data key
     * @param {any} value - Data value
     */
    storeData(key, value) {
        this.data.set(key, value);
    }
    
    /**
     * Retrieve stored data by key
     * @param {string} key - Data key
     * @returns {any} Stored data or undefined
     */
    getData(key) {
        return this.data.get(key);
    }
}

// Export functions and classes
module.exports = {
    calculateDiscount,
    fibonacciSequence,
    fetchUserData,
    Calculator,
    DataProcessor
};

// ES6 export syntax (for modern environments)
export {
    calculateDiscount,
    fibonacciSequence,
    fetchUserData,
    Calculator,
    DataProcessor
}; 
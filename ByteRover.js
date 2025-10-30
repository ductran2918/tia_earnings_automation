/**
 * ByteRover - Quicksort Implementation in JavaScript
 *
 * This module provides a quicksort algorithm implementation with various helper functions.
 */

/**
 * Main quicksort function
 * Sorts an array in-place using the quicksort algorithm
 *
 * @param {Array} arr - The array to sort
 * @param {number} low - Starting index (default: 0)
 * @param {number} high - Ending index (default: arr.length - 1)
 * @returns {Array} - The sorted array
 */
function quicksort(arr, low = 0, high = arr.length - 1) {
    if (low < high) {
        // Partition the array and get the pivot index
        const pivotIndex = partition(arr, low, high);

        // Recursively sort elements before and after partition
        quicksort(arr, low, pivotIndex - 1);
        quicksort(arr, pivotIndex + 1, high);
    }

    return arr;
}

/**
 * Partition function for quicksort
 * Places the pivot element at its correct position in sorted array
 * Places all smaller elements to left of pivot and all greater elements to right
 *
 * @param {Array} arr - The array to partition
 * @param {number} low - Starting index
 * @param {number} high - Ending index
 * @returns {number} - The final position of the pivot element
 */
function partition(arr, low, high) {
    // Choose the rightmost element as pivot
    const pivot = arr[high];

    // Index of smaller element (indicates the right position of pivot found so far)
    let i = low - 1;

    // Traverse through all elements and compare each with pivot
    for (let j = low; j < high; j++) {
        // If current element is smaller than or equal to pivot
        if (arr[j] <= pivot) {
            i++;
            // Swap arr[i] and arr[j]
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
    }

    // Swap arr[i + 1] and arr[high] (or pivot)
    [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];

    // Return the position from where partition is done
    return i + 1;
}

/**
 * Alternative quicksort implementation using different pivot selection
 * Uses the middle element as pivot
 *
 * @param {Array} arr - The array to sort
 * @returns {Array} - The sorted array
 */
function quicksortMiddlePivot(arr) {
    // Base case: arrays with 0 or 1 element are already sorted
    if (arr.length <= 1) {
        return arr;
    }

    // Choose middle element as pivot
    const pivotIndex = Math.floor(arr.length / 2);
    const pivot = arr[pivotIndex];

    // Partition array into three parts: less than pivot, equal to pivot, greater than pivot
    const left = [];
    const middle = [];
    const right = [];

    for (let element of arr) {
        if (element < pivot) {
            left.push(element);
        } else if (element === pivot) {
            middle.push(element);
        } else {
            right.push(element);
        }
    }

    // Recursively sort left and right partitions and combine
    return [...quicksortMiddlePivot(left), ...middle, ...quicksortMiddlePivot(right)];
}

/**
 * Quicksort with custom comparator function
 * Allows sorting with custom comparison logic
 *
 * @param {Array} arr - The array to sort
 * @param {Function} compareFn - Comparison function (a, b) => number
 * @returns {Array} - The sorted array
 */
function quicksortWithComparator(arr, compareFn = (a, b) => a - b) {
    if (arr.length <= 1) {
        return arr;
    }

    const pivot = arr[Math.floor(arr.length / 2)];
    const left = [];
    const middle = [];
    const right = [];

    for (let element of arr) {
        const comparison = compareFn(element, pivot);
        if (comparison < 0) {
            left.push(element);
        } else if (comparison === 0) {
            middle.push(element);
        } else {
            right.push(element);
        }
    }

    return [
        ...quicksortWithComparator(left, compareFn),
        ...middle,
        ...quicksortWithComparator(right, compareFn)
    ];
}

/**
 * Utility function to generate a random array for testing
 *
 * @param {number} size - Size of the array
 * @param {number} max - Maximum value (default: 100)
 * @returns {Array} - Random array of numbers
 */
function generateRandomArray(size, max = 100) {
    return Array.from({ length: size }, () => Math.floor(Math.random() * max));
}

/**
 * Utility function to check if an array is sorted
 *
 * @param {Array} arr - The array to check
 * @returns {boolean} - True if sorted, false otherwise
 */
function isSorted(arr) {
    for (let i = 1; i < arr.length; i++) {
        if (arr[i] < arr[i - 1]) {
            return false;
        }
    }
    return true;
}

// Export functions for use in other modules (Node.js)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        quicksort,
        partition,
        quicksortMiddlePivot,
        quicksortWithComparator,
        generateRandomArray,
        isSorted
    };
}

// Example usage and demonstration
if (require.main === module) {
    console.log('=== ByteRover Quicksort Demo ===\n');

    // Example 1: Basic quicksort
    const arr1 = [64, 34, 25, 12, 22, 11, 90];
    console.log('Original array:', arr1);
    quicksort(arr1);
    console.log('Sorted array (in-place):', arr1);
    console.log('Is sorted?', isSorted(arr1), '\n');

    // Example 2: Middle pivot quicksort
    const arr2 = [5, 2, 9, 1, 7, 6, 3];
    console.log('Original array:', arr2);
    const sorted2 = quicksortMiddlePivot(arr2);
    console.log('Sorted array (middle pivot):', sorted2);
    console.log('Is sorted?', isSorted(sorted2), '\n');

    // Example 3: Sort with custom comparator (descending order)
    const arr3 = [3, 7, 1, 9, 4];
    console.log('Original array:', arr3);
    const sorted3 = quicksortWithComparator(arr3, (a, b) => b - a);
    console.log('Sorted array (descending):', sorted3);
    console.log('Is sorted (descending)?', sorted3[0] >= sorted3[sorted3.length - 1], '\n');

    // Example 4: Sort objects by property
    const people = [
        { name: 'Alice', age: 30 },
        { name: 'Bob', age: 25 },
        { name: 'Charlie', age: 35 }
    ];
    console.log('Original people:', people);
    const sortedPeople = quicksortWithComparator(people, (a, b) => a.age - b.age);
    console.log('Sorted by age:', sortedPeople, '\n');

    // Example 5: Performance test with large array
    const largeArray = generateRandomArray(1000);
    console.log('Testing with large array (1000 elements)...');
    const startTime = Date.now();
    quicksort(largeArray);
    const endTime = Date.now();
    console.log(`Sorted in ${endTime - startTime}ms`);
    console.log('Is sorted?', isSorted(largeArray));
}

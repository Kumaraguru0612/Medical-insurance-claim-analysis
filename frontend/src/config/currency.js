/**
 * Centralized Currency Configuration & Indian Number Formatting Utilities
 * 
 * All monetary displays across MediClaim AI reference this single configuration file.
 * The underlying dataset and ML models retain their raw numeric values internally.
 */

// Centralized exchange rate (USD to INR)
export const USD_TO_INR = 95.43;

export const CURRENCY_CODE = 'INR';
export const CURRENCY_SYMBOL = '₹';
export const CURRENCY_NAME = 'Indian Rupee';

/**
 * Converts a raw USD amount to INR.
 * @param {number} usdVal - Amount in USD.
 * @returns {number} Amount in INR.
 */
export const convertUSDToINR = (usdVal) => {
  if (usdVal === null || usdVal === undefined || isNaN(usdVal)) return 0;
  return Number(usdVal) * USD_TO_INR;
};

/**
 * Formats a number using the standard Indian Numbering System (e.g., ₹12,66,396.18).
 * Grouping format: last 3 digits, then groups of 2 digits (e.g. 1,00,00,000).
 * 
 * @param {number} inrAmount - Amount in INR.
 * @param {object} options - Configuration options (decimals, includeSymbol, fallback).
 * @returns {string} Formatted Indian Rupee string.
 */
export const formatINR = (inrAmount, options = {}) => {
  const { decimals = 2, includeSymbol = true, fallback = '₹0' } = options;
  
  if (inrAmount === null || inrAmount === undefined || isNaN(inrAmount)) {
    return fallback;
  }

  const num = Number(inrAmount);
  const isNegative = num < 0;
  const absNum = Math.abs(num);

  let formattedInt = '';
  let formattedDec = '';

  if (decimals > 0) {
    const fixedStr = absNum.toFixed(decimals);
    const [intPart, decPart] = fixedStr.split('.');
    formattedInt = intPart;
    formattedDec = '.' + decPart;
  } else {
    formattedInt = Math.round(absNum).toString();
  }

  // Apply Indian comma grouping: 3, 2, 2, ...
  if (formattedInt.length > 3) {
    const last3 = formattedInt.slice(-3);
    let remaining = formattedInt.slice(0, -3);
    const groups = [];
    while (remaining.length > 2) {
      groups.unshift(remaining.slice(-2));
      remaining = remaining.slice(0, -2);
    }
    if (remaining.length > 0) {
      groups.unshift(remaining);
    }
    formattedInt = groups.join(',') + ',' + last3;
  }

  const symbol = includeSymbol ? `${CURRENCY_SYMBOL}` : '';
  const sign = isNegative ? '-' : '';

  return `${sign}${symbol}${formattedInt}${formattedDec}`;
};

/**
 * Formats an INR amount into executive-friendly compact Indian denominations:
 * - ₹X.XX Cr (Crores >= 1,00,00,000)
 * - ₹X.XX Lakh (Lakhs >= 1,00,000)
 * - ₹X,XXX (for thousands and below)
 * 
 * @param {number} inrAmount - Amount in INR.
 * @param {object} options - Formatting options.
 * @returns {string} Compact Indian currency representation (e.g., ₹169.44 Cr, ₹12.66 Lakh).
 */
export const formatCompactINR = (inrAmount, options = {}) => {
  const { includeSymbol = true, fullUnitName = false } = options;
  if (inrAmount === null || inrAmount === undefined || isNaN(inrAmount)) return '₹0';

  const num = Number(inrAmount);
  const isNegative = num < 0;
  const absNum = Math.abs(num);
  const symbol = includeSymbol ? `${CURRENCY_SYMBOL}` : '';
  const sign = isNegative ? '-' : '';

  if (absNum >= 10000000) {
    // 1 Crore = 10,000,000
    const crVal = (absNum / 10000000).toFixed(2);
    const unit = fullUnitName ? ' Crore' : ' Cr';
    return `${sign}${symbol}${crVal}${unit}`;
  } else if (absNum >= 100000) {
    // 1 Lakh = 100,000
    const lakhVal = (absNum / 100000).toFixed(2);
    const unit = fullUnitName ? ' Lakh' : ' Lakh';
    return `${sign}${symbol}${lakhVal}${unit}`;
  } else if (absNum >= 1000) {
    return `${sign}${formatINR(absNum, { includeSymbol, decimals: 0 })}`;
  } else {
    return `${sign}${formatINR(absNum, { includeSymbol, decimals: 2 })}`;
  }
};

/**
 * Helper to convert USD value to INR and return standard formatted string.
 * @param {number} usdVal - Value in USD.
 * @param {object} options - Format options.
 */
export const formatUSDToINR = (usdVal, options = {}) => {
  const inrVal = convertUSDToINR(usdVal);
  return formatINR(inrVal, options);
};

/**
 * Helper to convert USD value to INR and return compact formatted string (Lakh/Cr).
 * @param {number} usdVal - Value in USD.
 * @param {object} options - Format options.
 */
export const formatUSDToCompactINR = (usdVal, options = {}) => {
  const inrVal = convertUSDToINR(usdVal);
  return formatCompactINR(inrVal, options);
};

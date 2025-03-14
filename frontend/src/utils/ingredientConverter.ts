// Conversion factors
const CONVERSION_FACTORS = {
  // Volume conversions
  tsp: {
    ml: 4.93,
  },
  tbsp: {
    ml: 14.79,
    tsp: 3,
  },
  cup: {
    ml: 236.59,
    tbsp: 16,
  },
  oz: {
    ml: 29.57,
    g: 28.35, // approximate for liquids
  },
  floz: {
    ml: 29.57,
  },
  
  // Weight conversions
  lb: {
    g: 453.59,
  },
  kg: {
    g: 1000,
  },
};

// Density approximations (g/ml) for common ingredients
const INGREDIENT_DENSITIES: Record<string, number> = {
  // Liquids
  water: 1,
  milk: 1.03,
  cream: 1.02,
  'olive oil': 0.92,
  'vegetable oil': 0.92,
  'coconut oil': 0.92,
  vinegar: 1.01,
  honey: 1.42,
  syrup: 1.37,
  'maple syrup': 1.37,
  juice: 1.05,
  broth: 1,
  stock: 1,
  
  // Common solids by volume
  flour: 0.53,
  'all-purpose flour': 0.53,
  'bread flour': 0.53,
  sugar: 0.85,
  'brown sugar': 0.80,
  'granulated sugar': 0.85,
  'powdered sugar': 0.56,
  rice: 0.75,
  salt: 1.2,
  butter: 0.96,
  'shredded cheese': 0.45,
  'grated cheese': 0.55,
  oats: 0.40,
  yogurt: 1.03,
  
  // Fruits and vegetables (approximations)
  apple: 0.6,
  banana: 0.6,
  broccoli: 0.37,
  carrot: 0.64,
  zucchini: 0.7,
  potato: 0.68,
  tomato: 0.6,
  onion: 0.5,
  garlic: 0.5,
  spinach: 0.2,
};

// Determine if an ingredient is liquid
export function isLiquid(name: string): boolean {
  name = name.toLowerCase();
  const liquidIngredients = [
    'water', 'milk', 'cream', 'oil', 'juice', 'vinegar', 
    'sauce', 'broth', 'stock', 'wine', 'liquor', 'beer', 
    'extract', 'syrup', 'honey'
  ];
  
  return liquidIngredients.some(liquid => name.includes(liquid));
}

// Get density of an ingredient (g/ml)
export function getIngredientDensity(name: string): number {
  name = name.toLowerCase();
  
  // Check for exact matches
  if (INGREDIENT_DENSITIES[name]) {
    return INGREDIENT_DENSITIES[name];
  }
  
  // Check for partial matches
  for (const [ingredient, density] of Object.entries(INGREDIENT_DENSITIES)) {
    if (name.includes(ingredient)) {
      return density;
    }
  }
  
  // Default density if not found
  return isLiquid(name) ? 1.0 : 0.6;
}

// Parse fractions or mixed numbers (e.g., "1 1/2" or "1/4")
export function parseFraction(value: string): number {
  value = value.trim();
  
  // Check if it's already a number
  const numValue = parseFloat(value);
  if (!isNaN(numValue)) {
    return numValue;
  }
  
  // Check for mixed number (e.g., "1 1/2")
  const mixedMatch = value.match(/^(\d+)\s+(\d+)\/(\d+)$/);
  if (mixedMatch) {
    const whole = parseInt(mixedMatch[1]);
    const numerator = parseInt(mixedMatch[2]);
    const denominator = parseInt(mixedMatch[3]);
    return whole + (numerator / denominator);
  }
  
  // Check for simple fraction (e.g., "1/2")
  const fractionMatch = value.match(/^(\d+)\/(\d+)$/);
  if (fractionMatch) {
    const numerator = parseInt(fractionMatch[1]);
    const denominator = parseInt(fractionMatch[2]);
    return numerator / denominator;
  }
  
  // Return original value as number or 0 if invalid
  return isNaN(numValue) ? 0 : numValue;
}

// Convert volume units to milliliters
export function convertToMilliliters(amount: number, unit: string): number {
  unit = unit.toLowerCase().trim();
  
  switch (unit) {
    case 'ml':
    case 'milliliter':
    case 'milliliters':
      return amount;
    case 'l':
    case 'liter':
    case 'liters':
      return amount * 1000;
    case 'tsp':
    case 'teaspoon':
    case 'teaspoons':
      return amount * CONVERSION_FACTORS.tsp.ml;
    case 'tbsp':
    case 'tablespoon':
    case 'tablespoons':
      return amount * CONVERSION_FACTORS.tbsp.ml;
    case 'cup':
    case 'cups':
      return amount * CONVERSION_FACTORS.cup.ml;
    case 'oz':
    case 'fl oz':
    case 'fluid ounce':
    case 'fluid ounces':
      return amount * CONVERSION_FACTORS.oz.ml;
    default:
      return amount; // Return original amount if unit not recognized
  }
}

// Convert weight units to grams
export function convertToGrams(amount: number, unit: string): number {
  unit = unit.toLowerCase().trim();
  
  switch (unit) {
    case 'g':
    case 'gram':
    case 'grams':
      return amount;
    case 'kg':
    case 'kilogram':
    case 'kilograms':
      return amount * CONVERSION_FACTORS.kg.g;
    case 'lb':
    case 'pound':
    case 'pounds':
      return amount * CONVERSION_FACTORS.lb.g;
    case 'oz':
    case 'ounce':
    case 'ounces':
      return amount * CONVERSION_FACTORS.oz.g;
    default:
      return amount; // Return original amount if unit not recognized
  }
}

// Convert volume to weight using density
export function volumeToWeight(amount: number, unit: string, ingredientName: string): number {
  const volumeInMl = convertToMilliliters(amount, unit);
  const density = getIngredientDensity(ingredientName);
  return volumeInMl * density;
}

// Convert weight to volume using density
export function weightToVolume(amount: number, unit: string, ingredientName: string): number {
  const weightInGrams = convertToGrams(amount, unit);
  const density = getIngredientDensity(ingredientName);
  return weightInGrams / density;
}

// Format the amount in a user-friendly way
export function formatAmount(amount: number): string {
  // Handle whole numbers
  if (amount % 1 === 0) {
    return amount.toString();
  }
  
  // Handle decimals, limiting to 2 decimal places
  if (amount * 10 % 1 === 0) {
    return amount.toFixed(1);
  }
  
  return amount.toFixed(2);
}

// Get the best standard unit for an ingredient
export function getStandardUnit(ingredientName: string, originalUnit: string): string {
  const isIngredientLiquid = isLiquid(ingredientName);
  
  // If original unit is a weight unit and the ingredient is solid, keep it
  if (['g', 'gram', 'grams', 'kg', 'kilogram', 'kilograms', 'lb', 'pound', 'pounds', 'oz', 'ounce', 'ounces'].includes(originalUnit.toLowerCase()) && !isIngredientLiquid) {
    return originalUnit.toLowerCase().includes('gram') ? 'g' : originalUnit;
  }
  
  // If original unit is a volume unit and the ingredient is liquid, keep it
  if (['ml', 'milliliter', 'milliliters', 'l', 'liter', 'liters', 'cup', 'cups'].includes(originalUnit.toLowerCase()) && isIngredientLiquid) {
    // For small volumes, use ml; for larger volumes, use cups
    if (convertToMilliliters(1, originalUnit) < 50) {
      return 'ml';
    } else {
      return 'cup';
    }
  }
  
  // For liquids, prefer milliliters or cups
  if (isIngredientLiquid) {
    return 'ml';
  }
  
  // For solids, prefer grams
  return 'g';
}

// Standardize an ingredient's measurement
export function standardizeIngredientMeasurement(
  amount: number | string,
  unit: string,
  ingredientName: string
): { amount: number; unit: string } {
  // Parse the amount if it's a string
  const parsedAmount = typeof amount === 'string' ? parseFraction(amount) : amount;
  
  // Normalize the unit
  const normalizedUnit = unit.toLowerCase().trim();
  
  // Determine if the ingredient is liquid
  const isIngredientLiquid = isLiquid(ingredientName);
  
  // Get the best standard unit
  const standardUnit = getStandardUnit(ingredientName, normalizedUnit);
  
  let finalAmount = parsedAmount;
  
  // Convert to the standard unit
  if (isIngredientLiquid) {
    if (standardUnit === 'ml') {
      finalAmount = convertToMilliliters(parsedAmount, normalizedUnit);
    } else if (standardUnit === 'cup') {
      finalAmount = convertToMilliliters(parsedAmount, normalizedUnit) / CONVERSION_FACTORS.cup.ml;
    }
  } else {
    if (standardUnit === 'g') {
      // If original unit was a volume unit, convert to weight
      if (['tsp', 'teaspoon', 'teaspoons', 'tbsp', 'tablespoon', 'tablespoons', 'cup', 'cups', 'ml', 'milliliter', 'milliliters', 'l', 'liter', 'liters'].includes(normalizedUnit)) {
        finalAmount = volumeToWeight(parsedAmount, normalizedUnit, ingredientName);
      } else {
        finalAmount = convertToGrams(parsedAmount, normalizedUnit);
      }
    }
  }
  
  return {
    amount: finalAmount,
    unit: standardUnit,
  };
}

// Format an ingredient measurement in a readable format
export function formatIngredientMeasurement(
  amount: number,
  unit: string,
  ingredientName: string
): string {
  const formattedAmount = formatAmount(amount);
  
  // Determine if we need to add a space between the amount and unit
  const needsSpace = unit !== '';
  
  return `${formattedAmount}${needsSpace ? ' ' : ''}${unit}`;
} 
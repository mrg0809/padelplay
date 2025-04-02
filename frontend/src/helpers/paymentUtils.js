export const getBrandIcon = (brand) => {
    const icons = {
        visa: 'img:/icons/visa.svg', 
        mastercard: 'img:/icons/mastercard.svg',
        amex: 'img:/icons/amex.svg',
        // ... otras marcas
    };
    return icons[brand] || 'mdi-credit-card'; 
};

export const getBrandName = (brand) => {
    const names = {
        visa: 'Visa',
        mastercard: 'Mastercard',
        amex: 'American Express',
        // ...
    };
    return names[brand] || brand.charAt(0).toUpperCase() + brand.slice(1); 
};
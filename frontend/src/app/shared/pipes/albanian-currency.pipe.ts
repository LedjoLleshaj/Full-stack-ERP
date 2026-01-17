import { Pipe, PipeTransform } from '@angular/core';

/**
 * Formats currency amounts with appropriate symbols.
 * Usage: {{ amount | albanianCurrency:'EUR' }}
 */
@Pipe({
  name: 'albanianCurrency',
  standalone: true
})
export class AlbanianCurrencyPipe implements PipeTransform {
  private readonly currencySymbols: { [key: string]: string } = {
    'EUR': '€',
    'USD': '$',
    'LEK': 'Lek'
  };

  transform(
    value: number | string | null | undefined, 
    currency: string = 'EUR',
    showSymbol: boolean = true
  ): string {
    if (value == null) return '';
    
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    
    if (isNaN(numValue)) return '';
    
    const formattedValue = numValue.toFixed(2);
    const symbol = this.currencySymbols[currency] || currency;
    
    return showSymbol ? `${formattedValue} ${symbol}` : formattedValue;
  }
}

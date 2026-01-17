import { Pipe, PipeTransform } from '@angular/core';

/**
 * Formats dates in Albanian locale (sq-AL).
 * Usage: {{ dateStr | albanianDate }} or {{ dateStr | albanianDate:'short' }}
 */
@Pipe({
  name: 'albanianDate',
  standalone: true
})
export class AlbanianDatePipe implements PipeTransform {
  transform(
    value: string | Date | null | undefined,
    format: 'short' | 'medium' | 'long' | 'full' = 'medium'
  ): string {
    if (!value) return '';

    const date = typeof value === 'string' ? new Date(value) : value;
    
    if (isNaN(date.getTime())) return '';

    const options = this.getFormatOptions(format);
    return date.toLocaleDateString('sq-AL', options);
  }

  private getFormatOptions(format: string): Intl.DateTimeFormatOptions {
    switch (format) {
      case 'short':
        // "17 Jan"
        return { day: '2-digit', month: 'short' };
      case 'medium':
        // "17 Jan 2026"
        return { day: '2-digit', month: 'short', year: 'numeric' };
      case 'long':
        // "17 Janar 2026"
        return { day: '2-digit', month: 'long', year: 'numeric' };
      case 'full':
        // "E premte, 17 Janar 2026"
        return { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' };
      default:
        return { day: '2-digit', month: 'short', year: 'numeric' };
    }
  }
}

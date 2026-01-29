// Cookie utility service for managing authentication cookies
export class CookieService {
  /**
   * Delete a cookie by name
   */
  static deleteCookie(name: string): void {
    // Delete cookie for current path
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    
    // Also try to delete for root domain
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${window.location.hostname};`;
  }

  /**
   * Clear all authentication cookies
   */
  static clearAuthCookies(): void {
    this.deleteCookie('access_token');
    this.deleteCookie('refresh_token');
  }

  /**
   * Check if a cookie exists
   */
  static hasCookie(name: string): boolean {
    return document.cookie.split(';').some((item) => item.trim().startsWith(`${name}=`));
  }
}

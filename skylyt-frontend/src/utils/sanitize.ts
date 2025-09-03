/**
 * Sanitization utilities to prevent XSS and injection attacks
 */

/**
 * Sanitize string for safe logging to prevent log injection
 */
export const sanitizeForLogging = (input: any): string => {
  if (typeof input !== 'string') {
    input = String(input);
  }
  
  // Remove newlines, carriage returns, and other control characters
  return input
    .replace(/[\r\n\t\f\v]/g, ' ')
    .replace(/[\x00-\x1f\x7f-\x9f]/g, '')
    .trim();
};

/**
 * Sanitize HTML content to prevent XSS
 */
export const sanitizeHtml = (input: string): string => {
  if (typeof input !== 'string') return '';
  
  return input
    .replace(/[<>\"'&]/g, (match) => {
      const entities: Record<string, string> = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '&': '&amp;'
      };
      return entities[match] || match;
    });
};

/**
 * Sanitize input for safe JSON usage to prevent NoSQL injection
 */
export const sanitizeForJson = (input: any): any => {
  if (typeof input === 'string') {
    // Remove potential JSON injection characters
    return input.replace(/[\{\}\[\]"'\\]/g, '');
  }
  
  if (typeof input === 'object' && input !== null) {
    const sanitized: any = Array.isArray(input) ? [] : {};
    for (const key in input) {
      if (input.hasOwnProperty(key)) {
        sanitized[sanitizeForJson(key)] = sanitizeForJson(input[key]);
      }
    }
    return sanitized;
  }
  
  return input;
};

/**
 * Validate and sanitize user input
 */
export const validateAndSanitize = (input: string, maxLength: number = 1000): string => {
  if (typeof input !== 'string') return '';
  
  return sanitizeHtml(input.slice(0, maxLength));
};
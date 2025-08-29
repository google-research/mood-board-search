const { test, expect } = require('@playwright/test');

test.describe('Learn Concept Button Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the main page
    await page.goto('http://localhost:8080');
    
    // Wait for the page to load and data to populate
    await page.waitForTimeout(3000);
  });

  test('should find Try Concept buttons on the page', async ({ page }) => {
    // Look for Try Concept buttons
    const tryConceptButtons = page.locator('button:has-text("Try Concept")');
    
    // Should have at least one Try Concept button visible
    await expect(tryConceptButtons.first()).toBeVisible();
    
    // Count how many Try Concept buttons exist
    const buttonCount = await tryConceptButtons.count();
    console.log(`Found ${buttonCount} Try Concept buttons`);
    
    expect(buttonCount).toBeGreaterThan(0);
  });

  test('should navigate when Try Concept button is clicked', async ({ page }) => {
    // Wait for projects to load
    await page.waitForSelector('button:has-text("Try Concept")', { timeout: 10000 });
    
    // Find the first Try Concept button
    const firstTryButton = page.locator('button:has-text("Try Concept")').first();
    
    // Ensure button is visible and clickable
    await expect(firstTryButton).toBeVisible();
    
    // Get current URL before click
    const initialUrl = page.url();
    console.log('Initial URL:', initialUrl);
    
    // Click the Try Concept button
    await firstTryButton.click();
    
    // Wait for navigation to occur
    await page.waitForTimeout(2000);
    
    // Get URL after click
    const newUrl = page.url();
    console.log('New URL after click:', newUrl);
    
    // URL should have changed (navigation occurred)
    expect(newUrl).not.toBe(initialUrl);
    
    // Should navigate to a project URL (project ID format)
    expect(newUrl).toMatch(/\/project\//);
  });

  test('should have clickable button with proper styling', async ({ page }) => {
    await page.waitForSelector('button:has-text("Try Concept")', { timeout: 10000 });
    
    const tryButton = page.locator('button:has-text("Try Concept")').first();
    
    // Check button properties
    await expect(tryButton).toBeVisible();
    await expect(tryButton).toBeEnabled();
    
    // Check if button has expected CSS classes or styling
    const buttonClass = await tryButton.getAttribute('class');
    expect(buttonClass).toContain('try-button');
    
    // Check button text
    const buttonText = await tryButton.textContent();
    expect(buttonText.trim()).toBe('Try Concept');
  });

  test('should handle button click without errors', async ({ page }) => {
    // Listen for console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Listen for page errors
    const pageErrors = [];
    page.on('pageerror', error => {
      pageErrors.push(error.message);
    });

    await page.waitForSelector('button:has-text("Try Concept")', { timeout: 10000 });
    
    const tryButton = page.locator('button:has-text("Try Concept")').first();
    await tryButton.click();
    
    // Wait a moment for any async errors to surface
    await page.waitForTimeout(1000);
    
    // Debug: Log all console errors to understand what we're getting
    console.log('Console errors captured:', consoleErrors);
    
    // Check that no critical JavaScript errors occurred
    // Filter out development warnings which are expected
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('[Vue warn]') && 
      !error.includes('Download the Vue Devtools') &&
      !error.includes('source map') &&
      !error.includes('DevTools') &&
      !error.includes('404') // 404s might be expected
    );
    console.log('Critical errors after filtering:', criticalErrors);
    expect(criticalErrors.length).toBe(0);
    expect(pageErrors.length).toBe(0);
  });

  test('should work for multiple concept cards', async ({ page }) => {
    await page.waitForSelector('button:has-text("Try Concept")', { timeout: 10000 });
    
    const tryButtons = page.locator('button:has-text("Try Concept")');
    const buttonCount = await tryButtons.count();
    
    if (buttonCount > 1) {
      // Test clicking the second button if available
      const secondButton = tryButtons.nth(1);
      await expect(secondButton).toBeVisible();
      
      const initialUrl = page.url();
      await secondButton.click();
      await page.waitForTimeout(2000);
      
      const newUrl = page.url();
      expect(newUrl).not.toBe(initialUrl);
      expect(newUrl).toMatch(/\/project\//);
    }
  });
});
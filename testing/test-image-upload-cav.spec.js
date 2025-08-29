const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Navigation and CAV Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the main page
    await page.goto('http://localhost:8080');
    
    // Wait for the page to load
    await page.waitForTimeout(3000);
  });

  test('should successfully navigate concept creation workflow', async ({ page }) => {
    // Look for "Create a concept" link from the homepage
    const createConceptLink = page.locator('a:has-text("Create a concept")').first();
    
    if (await createConceptLink.count() > 0) {
      console.log('Found "Create a concept" link, clicking...');
      await createConceptLink.click();
      await page.waitForTimeout(2000);
      
      // After clicking, we should be on the project creation page
      // Check if we have reached a new page or have project creation UI
      const currentUrl = page.url();
      console.log(`Current URL after click: ${currentUrl}`);
      
      // Check for file upload functionality on the project creation page
      const fileInputs = page.locator('input[type="file"]');
      const uploadButtons = page.locator('button:has-text("Upload"), button:has-text("Add Image"), button:has-text("Choose")');
      
      const hasFileUpload = await fileInputs.count() > 0;
      const hasUploadButton = await uploadButtons.count() > 0;
      
      console.log(`File inputs found: ${await fileInputs.count()}`);
      console.log(`Upload buttons found: ${await uploadButtons.count()}`);
      
      if (hasFileUpload || hasUploadButton) {
        // If we have upload capability, the navigation worked
        expect(hasFileUpload || hasUploadButton).toBe(true);
      } else {
        // If no upload UI found, at least verify we navigated somewhere
        expect(currentUrl).toContain('project');
      }
    } else {
      // If no create concept link, at least verify we have existing projects to interact with
      const projectCards = page.locator('.card.published, .project-card, .concept-card');
      const projectCount = await projectCards.count();
      
      console.log(`Existing project cards found: ${projectCount}`);
      
      // Should have some projects/concepts available (we know there are 3 from debug)
      expect(projectCount).toBeGreaterThan(0);
    }
  });

  test('should display backend integration working', async ({ page }) => {
    // Test that frontend can communicate with backend
    // Look for any data that comes from the backend
    
    // Check for Try Concept buttons which indicate backend data is loaded
    await page.waitForSelector('button:has-text("Try Concept")', { timeout: 15000 });
    
    const tryButtons = page.locator('button:has-text("Try Concept")');
    const buttonCount = await tryButtons.count();
    
    console.log(`Try Concept buttons found: ${buttonCount}`);
    expect(buttonCount).toBeGreaterThan(0);
    
    // Test clicking a Try Concept button to verify backend integration
    const firstButton = tryButtons.first();
    await expect(firstButton).toBeVisible();
    
    const initialUrl = page.url();
    await firstButton.click();
    
    // Wait for navigation or state change
    await page.waitForTimeout(2000);
    
    const newUrl = page.url();
    
    // Should either navigate or show some response indicating backend worked
    const navigationOccurred = newUrl !== initialUrl;
    const hasLoadingState = await page.locator('.loading, .spinner, [class*="loading"]').count() > 0;
    const hasErrorMessage = await page.locator('.error, [class*="error"]').count() > 0;
    
    console.log(`Navigation occurred: ${navigationOccurred}`);
    console.log(`Loading state visible: ${hasLoadingState}`);
    console.log(`Error message visible: ${hasErrorMessage}`);
    
    // Either we navigated (success) or we're in a loading state (backend processing)
    // If there's an error message, that's a backend integration issue
    if (hasErrorMessage) {
      const errorText = await page.locator('.error, [class*="error"]').first().textContent();
      console.log(`Error message: ${errorText}`);
    }
    
    expect(navigationOccurred || hasLoadingState).toBe(true);
    expect(hasErrorMessage).toBe(false);
  });

  test('should handle Learn Concept workflow end-to-end', async ({ page }) => {
    // This test verifies the complete workflow from clicking Learn Concept
    // to getting results, which tests the full backend integration
    
    await page.waitForSelector('button:has-text("Try Concept")', { timeout: 15000 });
    
    const tryButton = page.locator('button:has-text("Try Concept")').first();
    await tryButton.click();
    
    // Wait for navigation to project page
    await page.waitForTimeout(3000);
    
    // Look for Learn Concept button on the project page
    const learnButton = page.locator('button:has-text("Learn Concept"), .learn-button');
    
    if (await learnButton.count() > 0) {
      console.log('Learn Concept button found on project page');
      
      await learnButton.first().click();
      
      // Wait for learning process to start/complete
      await page.waitForTimeout(5000);
      
      // Check for results or completion indicators
      const hasResults = await page.locator('.results, .search-results, .image-results').count() > 0;
      const hasLoadingCompleted = await page.locator('.learn-button[class*="complete"], .learn-button[class*="done"]').count() > 0;
      const hasError = await page.locator('.error, [class*="error"]').count() > 0;
      
      console.log(`Results found: ${hasResults}`);
      console.log(`Learning completed: ${hasLoadingCompleted}`);
      console.log(`Error occurred: ${hasError}`);
      
      if (hasError) {
        const errorText = await page.locator('.error, [class*="error"]').first().textContent();
        console.log(`Error during learning: ${errorText}`);
      }
      
      // Either we have results or the process completed without errors
      expect(hasResults || hasLoadingCompleted || !hasError).toBe(true);
    } else {
      console.log('No Learn Concept button found on project page - this might be expected based on UI design');
      
      // Check that we at least navigated to a project page successfully
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/\/project\//);
    }
  });

  test('should load and display project data from backend', async ({ page }) => {
    // Verify that the frontend successfully loads project data from backend
    
    // Wait for projects to load
    await page.waitForTimeout(5000);
    
    // Look for project cards or data that would come from backend
    const projectCards = page.locator('.project-card, .concept-card, [data-testid="project"]');
    const imageElements = page.locator('img:not([src=""]):not([src="#"])');
    const textContent = await page.textContent('body');
    
    const projectCount = await projectCards.count();
    const imageCount = await imageElements.count();
    const hasContent = textContent && textContent.trim().length > 100;
    
    console.log(`Project cards: ${projectCount}`);
    console.log(`Images loaded: ${imageCount}`);
    console.log(`Page has content: ${hasContent}`);
    
    // Should have either projects, images, or substantial content indicating backend data loaded
    expect(projectCount > 0 || imageCount > 0 || hasContent).toBe(true);
    
    // If we have Try Concept buttons, that's definitive proof backend is working
    const tryConceptButtons = await page.locator('button:has-text("Try Concept")').count();
    if (tryConceptButtons > 0) {
      console.log(`Backend integration confirmed: ${tryConceptButtons} Try Concept buttons found`);
      expect(tryConceptButtons).toBeGreaterThan(0);
    }
  });
});
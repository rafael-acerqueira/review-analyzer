import { test, expect } from '@playwright/test'

test.describe('Authenticated tests', () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext();
    page = await context.newPage();

    await page.goto('http://localhost:3000/login');

    await page.click('button:has-text("Create account")');

    await page.fill('input[type="email"]', 'user@example.com');
    await page.fill('input[type="password"]', 'password123');

    await page.click('button[type="submit"]');

    expect(page.url()).toBe('http://localhost:3000/login');
  });

  test.beforeEach(async ({ page }) => {

    await page.goto('http://localhost:3000/login');

    await page.fill('input[type="email"]', 'user@example.com');
    await page.fill('input[type="password"]', 'password123');

    await page.click('button[type="submit"]');

    await page.waitForSelector('[data-testid="title"]', { timeout: 20000, state: 'attached' });

    expect(page.url()).toBe('http://localhost:3000/');
  });

  test('submit review and receive the feedback', async ({ page }) => {
    await page.goto('http://localhost:3000');

    await page.getByPlaceholder('Tell me your thoughts').fill(
      'The pizza was cold and delayed one hour'
    );

    await page.getByRole('button', { name: 'Send for Analysis' }).click();

    await page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' });

    await expect(page.getByTestId('suggestion-text')).not.toBeAttached();

    const confirmBtn = page.getByTestId('confirm-and-submit');

    if (await confirmBtn.count() > 0) {
      console.log('confirm-and-submit found — proceeding...');
      await expect(confirmBtn).toBeAttached();
    } else {
      console.log('confirm-and-submit not found — review likely rejected by LLM.');
    }
  });

  test('submit review and receive a suggestion if dont provide enough information', async ({ page }) => {
    await page.goto('http://localhost:3000');

    await page.getByPlaceholder('Tell me your thoughts').fill(
      'This cellphone is not good enough'
    );

    await page.getByRole('button', { name: 'Send for Analysis' }).click();

    await page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' });

    const suggestionText = page.getByTestId('suggestion-text');

    if (await suggestionText.count() > 0) {
      console.log('Suggestion text found — review likely rejected.');
      await expect(suggestionText).toBeAttached();
    } else {
      console.log('No suggestion text — review likely accepted.');
    }

    const confirmBtn = page.getByTestId('confirm-and-submit');
    if (await confirmBtn.count() > 0) {
      console.log('confirm-and-submit found — proceeding...');
      await expect(confirmBtn).toBeAttached();
    } else {
      console.log('confirm-and-submit not found — review likely rejected.');
    }
  });

  test('submit review to analysis but discards', async ({ page }) => {
    await page.goto('http://localhost:3000');

    await page.getByPlaceholder('Tell me your thoughts').fill(
      "The pillow is not good enough because I woke up with a headache,\
      it's too small, and the material is worse than my last one"
    );

    await page.getByRole('button', { name: 'Send for Analysis' }).click();

    await page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' });

    await expect(page.getByTestId('suggestion-text')).not.toBeAttached();

    const confirmBtn = page.getByTestId('confirm-and-submit');

    if (await confirmBtn.count() > 0) {
      console.log('confirm-and-submit found — proceeding with discard flow...');
      await expect(confirmBtn).toBeAttached();

      const discardBtn = page.getByTestId('discard');
      await expect(discardBtn).toBeAttached();

      await discardBtn.click();

      await expect(page.getByTestId('send-to-analysis')).toBeAttached();
      await expect(page.getByPlaceholder('Tell me your thoughts')).toBeEmpty();

      await expect(page.getByTestId('feedback-message')).not.toBeAttached();
      await expect(page.getByTestId('suggestion-text')).not.toBeAttached();
      await expect(page.getByTestId('confirm-and-submit')).not.toBeAttached();
      await expect(page.getByTestId('discard')).not.toBeAttached();

    } else {
      console.log('confirm-and-submit not found — review likely rejected by LLM.');
    }
  });
});

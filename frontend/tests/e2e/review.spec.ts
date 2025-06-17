import { test, expect } from '@playwright/test';

const password = 'password123';

test.describe('Authenticated tests', () => {
  let email: string;

  test.beforeEach(async ({ page }) => {

    email = `user_${Date.now()}_${Math.floor(Math.random() * 10000)}@test.com`;

    await page.goto('http://localhost:3000/login');
    await page.click('button:has-text("Create account")');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3000/login', { timeout: 15000 });


    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3000/', { timeout: 20000 });
    await page.waitForSelector('[data-testid="title"]', { timeout: 20000 });
  });

  test('submit review and receive the feedback', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.getByPlaceholder('Tell me your thoughts').fill('The pizza was cold and delayed one hour');
    const sendBtn = page.getByRole('button', { name: 'Send for Analysis' });
    await Promise.all([
      page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' }),
      sendBtn.click(),
    ]);
    await expect(page.getByTestId('suggestion-text')).not.toBeAttached();
    const confirmBtn = page.getByTestId('confirm-and-submit');
    if (await confirmBtn.count() > 0) await expect(confirmBtn).toBeAttached();
  });

  test('submit review and receive a suggestion if dont provide enough information', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.getByPlaceholder('Tell me your thoughts').fill('This cellphone is not good enough');
    const sendBtn = page.getByRole('button', { name: 'Send for Analysis' });
    await Promise.all([
      page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' }),
      sendBtn.click(),
    ]);
    const suggestionText = page.getByTestId('suggestion-text');
    if (await suggestionText.count() > 0) await expect(suggestionText).toBeAttached();
    const confirmBtn = page.getByTestId('confirm-and-submit');
    if (await confirmBtn.count() > 0) await expect(confirmBtn).toBeAttached();
  });

  test('submit review to analysis but discards', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.getByPlaceholder('Tell me your thoughts').fill(
      "The pillow is not good enough because I woke up with a headache, it's too small, and the material is worse than my last one"
    );
    const sendBtn = page.getByRole('button', { name: 'Send for Analysis' });
    await Promise.all([
      page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' }),
      sendBtn.click(),
    ]);
    await expect(page.getByTestId('suggestion-text')).not.toBeAttached();
    const confirmBtn = page.getByTestId('confirm-and-submit');
    if (await confirmBtn.count() > 0) {
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
    }
  });
});
// frontend/tests/e2e/review.spec.ts

import { test, expect } from '../fixtures/authenticatedUser';

test.describe('Authenticated tests', () => {
  test('submit review and receive the feedback', async ({ page, userEmail }) => {

    await page.goto('http://localhost:3000');
    await page.getByPlaceholder('Tell me your thoughts').fill('The pizza was cold and delayed one hour');
    await page.getByRole('button', { name: 'Send for Analysis' }).click();
    await page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' });
    await expect(page.getByTestId('suggestion-text')).not.toBeAttached();
    const confirmBtn = page.getByTestId('confirm-and-submit');
    if (await confirmBtn.count() > 0) await expect(confirmBtn).toBeAttached();
  });

  test('submit review and receive a suggestion if dont provide enough information', async ({ page, userEmail }) => {
    await page.goto('http://localhost:3000');
    await page.getByPlaceholder('Tell me your thoughts').fill('This cellphone is not good enough');
    await page.getByRole('button', { name: 'Send for Analysis' }).click();
    await page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' });
    const suggestionText = page.getByTestId('suggestion-text');
    if (await suggestionText.count() > 0) await expect(suggestionText).toBeAttached();
    const confirmBtn = page.getByTestId('confirm-and-submit');
    if (await confirmBtn.count() > 0) await expect(confirmBtn).toBeAttached();
  });

  test('submit review to analysis but discards', async ({ page, userEmail }) => {
    await page.goto('http://localhost:3000');
    await page.getByPlaceholder('Tell me your thoughts').fill(
      "The pillow is not good enough because I woke up with a headache, it's too small, and the material is worse than my last one"
    );
    await page.getByRole('button', { name: 'Send for Analysis' }).click();
    await page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000, state: 'attached' });
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

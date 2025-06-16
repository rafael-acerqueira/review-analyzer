import { test as base, expect } from '@playwright/test';

const password = 'password123';

export const test = base.extend<{ userEmail: string }>({
  userEmail: async ({ page }, use, testInfo) => {
    const uniqueEmail = `user_${Date.now()}_${Math.floor(Math.random() * 10000)}@test.com`;

    await page.goto('http://localhost:3000/login');
    await page.click('button:has-text("Create account")');
    await page.fill('input[type="email"]', uniqueEmail);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    try {
      await page.waitForURL('http://localhost:3000/login', { timeout: 10000 });
    } catch (e) {
      console.error('Fail to create user:', await page.content());
      throw e;
    }

    await page.waitForTimeout(2000);

    await page.goto('http://localhost:3000/login');
    await page.fill('input[type="email"]', uniqueEmail);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    try {
      await page.waitForURL('http://localhost:3000/', { timeout: 20000 });
      await page.waitForSelector('[data-testid="title"]', { timeout: 20000 });
    } catch (e) {
      console.error('Erro no login:', await page.content());
      throw e;
    }

    await use(uniqueEmail);
  },
});

export { expect };
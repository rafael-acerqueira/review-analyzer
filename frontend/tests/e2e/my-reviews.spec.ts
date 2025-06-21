import { test, expect } from '@playwright/test'

test('User submits review and sees it in "Meus Reviews"', async ({ page }) => {

  const email = `user_${Date.now()}@test.com`
  const password = 'password123'

  await page.goto('http://localhost:3000/login')
  await page.click('button:has-text("Create account")')
  await page.fill('input[type="email"]', email)
  await page.fill('input[type="password"]', password)
  await page.click('button[type="submit"]')

  await page.fill('input[type="email"]', email)
  await page.fill('input[type="password"]', password)
  await page.click('button[type="submit"]')
  await page.waitForURL('http://localhost:3000/')

  const review = "This cellphone is pretty slow when I send emails and need to  \
                  access social media. Also, I have calls with my clients all \
                  day and the battery doesn't charge as soon as I need"

  await page.getByPlaceholder('Tell me your thoughts').fill(review)
  await page.getByRole('button', { name: 'Send for Analysis' }).click()
  await page.waitForSelector('[data-testid="feedback-message"]', { timeout: 20000 })

  await page.getByRole('button', { name: 'Confirm and Submit' }).click()

  await page.waitForTimeout(1000);

  await page.goto('http://localhost:3000/my-reviews')
  await expect(page).toHaveURL(/my-reviews/)

  await expect(page.locator(`text=${review}`)).toBeVisible()
  await page.screenshot({ path: 'debug.png' })
})

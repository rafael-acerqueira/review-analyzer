import { test, expect } from '@playwright/test'

test('submit review and receive the feedback', async ({ page }) => {
  await page.goto('http://localhost:3000')

  await page.getByPlaceholder('Tell me your thoughts').fill(
    'The pizza was cold and delayed one hour'
  )

  await page.getByRole('button', { name: 'Send for Analysis' }).click()

  await expect(page.getByTestId('feedback-message')).toBeVisible()
  await expect(page.getByTestId('sugestion-text')).not.toBeVisible()
  await expect(page.getByTestId('confirm-and-submit')).toBeVisible()
})

test('submit review and receive a suggestion if dont provide enough information', async ({ page }) => {
  await page.goto('http://localhost:3000')

  await page.getByPlaceholder('Tell me your thoughts').fill(
    'This cellphone is not good enough'
  )

  await page.getByRole('button', { name: 'Send for Analysis' }).click()

  await expect(page.getByTestId('feedback-message')).toBeVisible()
  await expect(page.getByTestId('sugestion-text')).toBeVisible()
  await expect(page.getByTestId('confirm-and-submit')).not.toBeVisible()

})


test('submit review to analysis but discards', async ({ page }) => {
  await page.goto('http://localhost:3000')

  await page.getByPlaceholder('Tell me your thoughts').fill(
    "The pillow is not good enough because I woke up with a headache,\
    it's too small, and the material is worse than my last one"
  )

  await page.getByRole('button', { name: 'Send for Analysis' }).click()

  await expect(page.getByTestId('feedback-message')).toBeVisible()
  await expect(page.getByTestId('sugestion-text')).not.toBeVisible()
  await expect(page.getByTestId('confirm-and-submit')).toBeVisible()
  await expect(page.getByTestId('discard')).toBeVisible()

  await page.getByTestId('discard').click()

  await expect(page.getByTestId('send-to-analysis')).toBeVisible()
  await expect(page.getByPlaceholder('Tell me your thoughts')).toBeEmpty()
  await expect(page.getByTestId('feedback-message')).not.toBeVisible()
  await expect(page.getByTestId('sugestion-text')).not.toBeVisible()
  await expect(page.getByTestId('confirm-and-submit')).not.toBeVisible()
  await expect(page.getByTestId('discard')).not.toBeVisible()

})
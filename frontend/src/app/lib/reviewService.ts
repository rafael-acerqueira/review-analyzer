export type ReviewPayload = {
  text: string
}

export type Review = {
  text: string,
  sentiment: string,
  status: string,
  feedback: string,
  suggestion?: string
}

export async function submitReviewRequest(payload: ReviewPayload) {
  const response = await fetch("/api/submit-review-proxy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error("Error when analyze the review")
  return response.json()
}

export async function createReview(payload: Review) {
  const response = await fetch("/api/create-review-proxy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error("We got an error during the review store")
  return response.json()
}

export async function listReview() {
  const response = await fetch("/api/list-review-proxy", {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  })
  if (!response.ok) throw new Error("We got an error listing the reviews")
  return response.json()
}
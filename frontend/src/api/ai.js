import client from './client'

export const aiApi = {
  analyzeJd: (jdText, resumeText = null) =>
    client.post('/ai/analyze-jd', { jd_text: jdText, resume_text: resumeText }),
  generateQuestions: (position, jdText, questionCount = 10) =>
    client.post('/ai/generate-questions', { position, jd_text: jdText, question_count: questionCount }),
  mockInterview: (history, userAnswer) =>
    client.post('/ai/mock-interview', { history, user_answer: userAnswer }),
  estimateCalories: (foodDescription) =>
    client.post('/ai/estimate-calories', { food_description: foodDescription }),
  dailyAdvice: (jobSummary, fitnessSummary) =>
    client.post('/ai/daily-advice', { job_summary: jobSummary, fitness_summary: fitnessSummary }),
}

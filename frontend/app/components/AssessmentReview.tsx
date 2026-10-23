export type SavedAnswer = {
  question_id: string; statement: string; option_id: string; correct: boolean;
  selected_option: string; correct_answer: string; explanation: string;
  feedback: string; suspected_misconception: string | null;
  corrective_guidance?: string; teaching_recommendation?: string;
  verification_method?: "ai_assisted" | "manual_fallback";
};
export type SavedResult = {
  title: string; topics: string[]; status: string; question_count: number;
  correct: number; incorrect: number; percentage: number; completed_at: string | null;
  answers: SavedAnswer[];
};
export default function AssessmentReview({ result }: { result: SavedResult }) {
  return <section className="panel">
    <h2>{result.title} — {result.status}</h2><p>{result.topics.join(", ")}</p>
    <p>{result.correct}/{result.question_count} ({result.percentage}%) · {result.correct} correct · {result.incorrect} incorrect</p>
    {result.completed_at && <p>Completed {new Date(result.completed_at).toLocaleString()}</p>}
    {result.answers.map(answer => <article className="feedback-box review" key={answer.question_id}>
      <h3>{answer.statement}</h3><p>{answer.correct ? "Correct" : "Incorrect"} · Your answer: {answer.selected_option}</p>
      <p>Correct answer: {answer.correct_answer}</p><p>{answer.explanation}</p><p>{answer.feedback}</p>
      {answer.suspected_misconception && <p>Possible misconception: {answer.suspected_misconception}</p>}
      {answer.corrective_guidance && <p>Learning tip: {answer.corrective_guidance}</p>}
      {answer.teaching_recommendation && <p>Recommended practice: {answer.teaching_recommendation}</p>}
    </article>)}
    <p className="helper">Wrong answers suggest possible misconceptions; they do not prove them.</p>
  </section>;
}

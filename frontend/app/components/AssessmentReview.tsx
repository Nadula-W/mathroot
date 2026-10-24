"use client";

import { TranslationWarning, useLanguage } from "../../lib/i18n/LanguageProvider";
import type { Translatable } from "../../lib/i18n/core";

export type SavedAnswer = Translatable & {
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
  const { t, topic, content, locale } = useLanguage();
  return <section className="panel">
    <h2>{result.title} — {t(result.status)}</h2><p>{result.topics.map(topic).join(", ")}</p>
    <p>{result.correct}/{result.question_count} ({result.percentage}%) · {t("{correct} correct · {incorrect} incorrect", { correct: result.correct, incorrect: result.incorrect })}</p>
    {result.completed_at && <p>{t("Completed {date}", { date: new Date(result.completed_at).toLocaleString(locale) })}</p>}
    {result.answers.map(answer => <article className="feedback-box review" key={answer.question_id}>
      <h3>{content(answer, "statement")}</h3><p>{t(answer.correct ? "Correct" : "Incorrect")} · {t("Your answer:")} {content(answer, "selected_option")}</p>
      <p>{t("Correct answer:")} {content(answer, "correct_answer")}</p><p>{content(answer, "explanation")}</p><p>{content(answer, "feedback")}</p>
      {answer.suspected_misconception && <p>{t("Possible misconception:")} {t(answer.suspected_misconception)}</p>}
      {answer.corrective_guidance && <p>{t("Learning tip:")} {content(answer, "corrective_guidance")}</p>}
      {answer.teaching_recommendation && <p>{t("Recommended practice:")} {content(answer, "teaching_recommendation")}</p>}
      <TranslationWarning record={answer} />
    </article>)}
    <p className="helper">{t("Wrong answers suggest possible misconceptions; they do not prove them.")}</p>
  </section>;
}

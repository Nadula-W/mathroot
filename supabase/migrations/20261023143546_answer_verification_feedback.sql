-- Nullable: preserve existing answer records without backfilling or regrading.
alter table public.mathroot_answers
  add column if not exists verification jsonb;

comment on column public.mathroot_answers.verification is
  'Server-generated immutable feedback snapshot, method, confidence and diagnostic metadata. Legacy answers may be null.';

-- Existing RLS and backend-only table privileges remain unchanged.

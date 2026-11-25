-- Optional seed data for the global question-of-the-day pool.
-- The app also seeds these automatically if the table is empty.

INSERT INTO daily_prompts (chat_id, kind, text_ru, text_en, options_ru, options_en) VALUES
    (NULL, 'question', 'Какой навык вы хотели бы освоить в этом году?', 'What skill would you love to learn this year?', NULL, NULL),
    (NULL, 'question', 'Фильм или сериал, который недавно зацепил — почему?', 'A movie or show that recently hooked you — why?', NULL, NULL),
    (NULL, 'question', 'Расскажите о маленькой победе за эту неделю 🎉', 'Share a small win from your week 🎉', NULL, NULL),
    (NULL, 'poll', 'Как вам больше нравится работать?', 'How do you prefer to work?', 'Утром|Днём|Вечером|Ночью', 'Morning|Afternoon|Evening|Night'),
    (NULL, 'poll', 'Кофе или чай?', 'Coffee or tea?', 'Кофе|Чай|Ни то, ни другое', 'Coffee|Tea|Neither');

# Detailed Changelogs

Эта директория содержит детальные changelogs для отдельных крупных изменений.

## Доступные changelogs

- [my-transit-enhanced.md](my-transit-enhanced.md) - Улучшения команды /my_transit

## Назначение

Основной [CHANGELOG.md](../../CHANGELOG.md) содержит краткую информацию о всех изменениях.

Эта директория содержит **детальные технические changelog'и** для крупных изменений:
- Подробное описание всех модификаций
- Технические детали реализации
- Тестовые checklist'ы
- Related files
- Backward compatibility notes

## Когда создавать детальный changelog

Создавайте отдельный changelog когда:
1. Изменение затрагивает множество файлов
2. Требуется детальная техническая документация
3. Есть breaking changes
4. Нужны migration notes

## Naming Convention

Файлы именуются описательно через дефис (lowercase):
- `feature-name-implementation.md`
- `major-refactoring-notes.md`
- `api-migration-guide.md`

**Важно:** Всегда обновляйте основной CHANGELOG.md, а не создавайте новые changelog файлы для мелких изменений.


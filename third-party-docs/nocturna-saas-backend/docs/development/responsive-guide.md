# Руководство по адаптивности Nocturna

## Обзор

Приложение Nocturna полностью адаптивно и использует mobile-first подход. Это означает, что базовые стили написаны для мобильных устройств, а затем прогрессивно улучшаются для больших экранов.

## Breakpoints (Точки перелома)

Приложение использует следующие breakpoints:

- **Mobile**: 320px - 575px (базовые стили)
- **Tablet**: 576px - 767px
- **Tablet Landscape**: 768px - 991px
- **Desktop**: 992px - 1199px
- **Large Desktop**: 1200px - 1399px
- **Extra Large**: 1400px+

## Структура CSS

### Основные файлы стилей

1. **`responsive.css`** - Основные адаптивные стили (mobile-first)
2. **`mobile-forms.css`** - Специальные стили для форм на мобильных устройствах
3. **`chart-responsive.css`** - Адаптивные стили для астрологических карт
4. **`interpretation.css`** - Обновленные адаптивные стили для интерпретаций

### CSS Custom Properties

```css
:root {
  /* Breakpoints */
  --breakpoint-sm: 576px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 992px;
  --breakpoint-xl: 1200px;
  --breakpoint-xxl: 1400px;

  /* Spacing Scale */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-xxl: 3rem;

  /* Component Sizes */
  --form-padding-mobile: 1rem;
  --form-padding-tablet: 1.5rem;
  --form-padding-desktop: 2rem;
  --chart-height-mobile: 300px;
  --chart-height-tablet: 400px;
  --chart-height-desktop: 500px;
}
```

## Ключевые особенности

### 1. Mobile-First подход

Все стили начинаются с мобильной версии и расширяются для больших экранов:

```css
/* Базовые мобильные стили */
.form-container {
  padding: 1rem;
  border-radius: 12px;
}

/* Планшеты */
@media (min-width: 576px) {
  .form-container {
    padding: 1.5rem;
    border-radius: 14px;
  }
}

/* Десктопы */
@media (min-width: 992px) {
  .form-container {
    padding: 2rem;
    border-radius: 16px;
  }
}
```

### 2. Touch-friendly интерфейс

- Минимальный размер кнопок и интерактивных элементов: 44px (рекомендация Apple)
- Размер шрифта не менее 16px для предотвращения зума на iOS
- Увеличенные отступы для удобства касания

### 3. Адаптивная навигация

- На мобильных: компактное меню с гамбургером
- На планшетах: горизонтальное меню
- На десктопах: полноценная навигация

### 4. Гибкая сетка

Использует Bootstrap Grid с дополнительными адаптивными классами:

```tsx
<Row className="g-4">
  <Col xs={12} md={5}>
    {/* Форма */}
  </Col>
  <Col xs={12} md={7}>
    {/* Карта */}
  </Col>
</Row>
```

### 5. Utility классы

```css
/* Показать только на мобильных */
.d-mobile-only

/* Показать только на планшетах и выше */
.d-tablet-up

/* Адаптивный текст */
.text-responsive

/* Адаптивные отступы */
.spacing-responsive
```

## Компоненты

### Navigation

- Адаптивное меню с коллапсом на мобильных
- Sticky позиционирование
- Touch-friendly кнопки

### Forms

- Увеличенные поля ввода на мобильных
- Адаптивная валидация
- Touch-friendly элементы управления

### Charts

- Масштабируемые SVG
- Адаптивные легенды
- Touch-friendly зум и панорамирование

### Interpretation

- Вертикальные табы на мобильных
- Горизонтальные табы на десктопах
- Адаптивная высота контента

## Тестирование

### Браузерные инструменты

1. Откройте DevTools (F12)
2. Включите Device Toolbar (Ctrl+Shift+M)
3. Тестируйте различные размеры экранов

### Тестовая страница

Перейдите на `/responsive-test` для просмотра демонстрации адаптивности.

### Рекомендуемые размеры для тестирования

- iPhone SE: 375x667
- iPhone 12: 390x844
- iPad: 768x1024
- iPad Pro: 1024x1366
- Desktop: 1920x1080

## Accessibility (Доступность)

### Поддержка клавиатуры

- Все интерактивные элементы доступны с клавиатуры
- Видимые индикаторы фокуса
- Логичный порядок табуляции

### Поддержка скринридеров

- Семантическая разметка
- ARIA-атрибуты где необходимо
- Альтернативный текст для изображений

### Поддержка уменьшенной анимации

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Высокий контраст

```css
@media (prefers-contrast: high) {
  .form-container {
    border: 2px solid #000;
  }
}
```

## Производительность

### Оптимизация изображений

- Адаптивные изображения с srcset
- WebP формат с fallback
- Lazy loading для изображений

### CSS оптимизация

- Минификация в production
- Критический CSS inline
- Удаление неиспользуемых стилей

### JavaScript оптимизация

- Code splitting по маршрутам
- Lazy loading компонентов
- Оптимизация bundle size

## Лучшие практики

### 1. Всегда начинайте с мобильной версии

```css
/* ✅ Правильно */
.component {
  /* мобильные стили */
}

@media (min-width: 768px) {
  .component {
    /* стили для больших экранов */
  }
}

/* ❌ Неправильно */
.component {
  /* десктопные стили */
}

@media (max-width: 767px) {
  .component {
    /* мобильные стили */
  }
}
```

### 2. Используйте относительные единицы

```css
/* ✅ Правильно */
padding: 1rem;
font-size: 1.2em;
width: 100%;

/* ❌ Избегайте */
padding: 16px;
font-size: 20px;
width: 320px;
```

### 3. Тестируйте на реальных устройствах

- Используйте BrowserStack или подобные сервисы
- Тестируйте на медленных соединениях
- Проверяйте touch-взаимодействия

### 4. Оптимизируйте производительность

- Минимизируйте количество медиа-запросов
- Используйте CSS Grid и Flexbox
- Избегайте фиксированных размеров

## Troubleshooting

### Проблемы с viewport

Убедитесь, что в HTML есть правильный viewport meta tag:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

### Проблемы с iOS Safari

- Используйте `-webkit-appearance: none` для кастомных элементов
- Тестируйте зум при фокусе на input
- Проверяйте поведение в landscape режиме

### Проблемы с Android

- Тестируйте на разных версиях Android
- Проверяйте поведение системной навигации
- Учитывайте различия в рендеринге

## Заключение

Адаптивность - это не просто изменение размеров, это создание оптимального пользовательского опыта для каждого устройства. Следуя этому руководству, вы сможете поддерживать и развивать адаптивность приложения Nocturna. 
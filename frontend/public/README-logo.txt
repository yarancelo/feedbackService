Положите сюда логотип с именем logo.svg (или logo.png и поправьте src в
src/pages/FeedbackForm.jsx). Файл автоматически появится в шапке формы.
Vite копирует содержимое public/ в корень сайта, поэтому /logo.svg будет доступен.

Фирменный шрифт меняется в двух местах:
  1) index.html — тег <link> с Google Fonts (или подключите свой @font-face);
  2) src/styles/index.css — переменные --serif / --sans / --mono.

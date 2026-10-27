import js from '@eslint/js'
import boundaries from 'eslint-plugin-boundaries'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import tseslint from 'typescript-eslint'

const MENSAGEM_DO_TRAVESSAO =
  'Sem travessão nem meia-risca: use vírgula, dois-pontos, parênteses ou "a" (docs/padroes-de-codigo.md).'

const CAMADAS = [
  { type: 'domain', pattern: 'src/domain' },
  { type: 'application', pattern: 'src/application' },
  { type: 'infrastructure', pattern: 'src/infrastructure' },
  { type: 'montagem', pattern: 'src/ui/app' },
  { type: 'graficos', pattern: 'src/ui/charts' },
  { type: 'mapa', pattern: 'src/ui/map' },
  { type: 'ui', pattern: 'src/ui' },
]

const INTERFACE = ['ui', 'graficos', 'mapa']

export default defineConfig([
  globalIgnores(['dist', 'coverage']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.strict,
      reactHooks.configs.flat['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: { ecmaVersion: 2023, globals: globals.browser },
    rules: {
      'no-restricted-syntax': [
        'error',
        { selector: 'Literal[value=/[\\u2013\\u2014]/]', message: MENSAGEM_DO_TRAVESSAO },
        {
          selector: 'TemplateElement[value.raw=/[\\u2013\\u2014]/]',
          message: MENSAGEM_DO_TRAVESSAO,
        },
        { selector: 'JSXText[value=/[\\u2013\\u2014]/]', message: MENSAGEM_DO_TRAVESSAO },
      ],
    },
  },
  {
    files: ['src/**/*.{ts,tsx}'],
    ignores: ['**/*.test.{ts,tsx}', 'src/testes/**', 'src/main.tsx'],
    plugins: { boundaries },
    settings: {
      'import/resolver': { typescript: { alwaysTryTypes: true } },
      'boundaries/elements': CAMADAS,
    },
    rules: {
      'boundaries/dependencies': [
        'error',
        {
          default: 'disallow',
          checkAllOrigins: true,
          message:
            '{{from.element.types}} não pode depender de {{to.element.types}}{{to.module.source}} (docs/clean-architecture.md).',
          policies: [
            {
              from: { element: { type: 'domain' } },
              allow: { to: { element: { type: 'domain' } } },
            },
            {
              from: { element: { type: 'application' } },
              allow: { to: { element: { types: ['domain', 'application'] } } },
            },
            {
              from: { element: { type: 'infrastructure' } },
              allow: { to: { element: { types: ['domain', 'application', 'infrastructure'] } } },
            },
            {
              from: { element: { types: INTERFACE } },
              allow: { to: { element: { types: ['domain', 'application', ...INTERFACE] } } },
            },
            {
              from: { element: { type: 'montagem' } },
              allow: {
                to: {
                  element: {
                    types: ['domain', 'application', 'infrastructure', 'montagem', ...INTERFACE],
                  },
                },
              },
            },
            {
              from: {
                element: { types: ['application', 'infrastructure', 'montagem', ...INTERFACE] },
              },
              allow: { to: { module: { origin: 'external' } } },
            },
            {
              from: { element: { type: 'domain' } },
              disallow: { to: { module: { origin: 'external' } } },
              message:
                'O domínio não importa biblioteca externa, nem React (docs/clean-architecture.md).',
            },
            {
              from: { element: { type: '!graficos' } },
              disallow: { to: { module: { origin: 'external', source: 'recharts' } } },
            },
            {
              from: { element: { type: '!mapa' } },
              disallow: { to: { module: { origin: 'external', source: 'leaflet' } } },
            },
          ],
        },
      ],
    },
  },
])

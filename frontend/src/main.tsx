import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './ui/theme/tokens.css'
import './ui/theme/base.css'
import { App } from './ui/app/App'

const raiz = document.getElementById('raiz')
if (!raiz) throw new Error('O elemento #raiz não existe em index.html')

createRoot(raiz).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

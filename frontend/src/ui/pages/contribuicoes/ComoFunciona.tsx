import estilos from './Contribuicoes.module.css'

const REGRAS = [
  {
    titulo: 'Soma sozinho',
    texto:
      'Mesmo endereço com número, mesmo serviço e até 7 dias de diferença. O novo relato vira mais um na mesma ocorrência.',
  },
  {
    titulo: 'Vem para esta tela',
    texto:
      'Rua, número ou serviço parecidos, com menos de 30 dias de diferença. Pontuação: local 60%, serviço 20%, tempo 15% e detalhe 5%. A partir de 72%, a dupla espera a sua decisão.',
  },
  {
    titulo: 'Fica separado',
    texto:
      'Outro bairro, outro tema, pontuação menor ou 30 dias ou mais. Depois de 30 dias, o problema voltou: é reincidência e nunca é apagada.',
  },
  {
    titulo: 'Na importação',
    texto:
      'Todo arquivo manual é comparado com estes relatos, e todo pacote é comparado com a base pelo pseudônimo do endereço. Coincidência vira pendência, e nada entra sem decisão.',
  },
] as const

export function ComoFunciona() {
  return (
    <div className={estilos.regras}>
      {REGRAS.map(({ titulo, texto }) => (
        <article key={titulo}>
          <h3>{titulo}</h3>
          <p>{texto}</p>
        </article>
      ))}
    </div>
  )
}

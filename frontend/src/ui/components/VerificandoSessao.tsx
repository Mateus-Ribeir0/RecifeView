import estilos from './VerificandoSessao.module.css'

export function VerificandoSessao() {
  return (
    <div className={estilos.verificando} role="status">
      Verificando a sua sessão...
    </div>
  )
}

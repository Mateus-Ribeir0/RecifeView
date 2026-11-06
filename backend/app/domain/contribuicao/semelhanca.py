def _trigramas(texto: str) -> frozenset[str]:
    grupos: set[str] = set()
    for palavra in texto.split():
        cercada = f"  {palavra} "
        grupos.update(cercada[inicio : inicio + 3] for inicio in range(len(cercada) - 2))
    return frozenset(grupos)


def semelhanca_de_texto(primeiro: str, segundo: str) -> float:
    """Coeficiente de Dice sobre trigramas: tolera erro de digitação e palavras em outra ordem."""
    grupos_do_primeiro, grupos_do_segundo = _trigramas(primeiro), _trigramas(segundo)
    if not grupos_do_primeiro or not grupos_do_segundo:
        return 0.0
    comuns = len(grupos_do_primeiro & grupos_do_segundo)
    return 2 * comuns / (len(grupos_do_primeiro) + len(grupos_do_segundo))

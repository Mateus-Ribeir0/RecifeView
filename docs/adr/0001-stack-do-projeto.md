# 0001. Usar React, FastAPI, PostgreSQL e um Processor agendado no EventBridge

- **Status:** aceita
- **Data:** 26/10/2026
- **Quem decidiu:** grupo, a partir do esboço de arquitetura do Prof. Marcelo

## Contexto

A Proposição de Projeto (Semana 5) e a N1 citavam "Streamlit ou Power BI" como ferramenta de publicação, com a escolha prevista para a N5. Depois, na reunião de alinhamento, o Prof. Marcelo desenhou uma arquitetura de aplicação real: o painel precisa de login para gestores públicos e de ingestão periódica dos dados da Prefeitura, coisas que um Streamlit ou um Power BI publicado não resolvem bem. O C4 v0.1 (15/10/2026) registrou esse esboço.

## Opções consideradas

| Opção | A favor | Contra |
|---|---|---|
| Streamlit | Rápido de montar, tudo em Python | Autenticação e controle de acesso limitados; pouco controle visual sobre a identidade do RecifeView |
| Power BI Web | Ferramenta conhecida de gestão pública | Licença, publicação de dado sensível e pouca liberdade para o pipeline e o login próprios |
| SPA + API + banco + job agendado | Login, auditoria, identidade visual própria, pipeline automatizado; é a arquitetura do esboço do orientador | Mais partes para construir e manter |

## Decisão

| Camada | Tecnologia |
|---|---|
| Frontend | SPA em React, Recharts para gráficos e Leaflet para o mapa coroplético |
| Backend | API REST em Python com FastAPI |
| Banco | PostgreSQL |
| Processor | Script Python agendado (cron) por regras do AWS EventBridge, que ingere e transforma os dados da Prefeitura periodicamente |

O Streamlit pode servir de protótipo rápido, mas não é o produto.

## Consequências

- A N5 (Proposta de Integração e Publicação) passa a descrever esta arquitetura em vez de escolher entre ferramentas de BI.
- O pipeline do Drive (`pipeline.py`, `build_dataset.py`) vira a base do Processor.
- Ficam em aberto: onde guardar a camada bruta, onde roda o Processor, como autenticar e as ferramentas complementares. Ver [README.md](README.md#decisões-em-aberto).
- O grupo precisa dividir o trabalho entre três frentes (frontend, backend e processor), além da análise.

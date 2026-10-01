# Honda City EXL 2025 — candidata FrogPilot

**Candidata experimental instalada e observada em bancada em 01/10/2026. Reconhecimento no veículo e condução ainda não validados nesta candidata.**

Preparada em 30/09/2026 e instalada em bancada em 01/10/2026. Repositório: N30-PH/FrogPilot, branch `FrogPilot-City-7G`.

## Instalação observada no aparelho do proprietário

Commit instalado: [`51ccaf8fa6706c841c783c17e7c787616d916d08`](https://github.com/N30-PH/FrogPilot/commit/51ccaf8fa6706c841c783c17e7c787616d916d08). As atualizações posteriores deste README são documentação; não representam atualização automática do aparelho.

- comma 3X: AGNOS 10.1/A → **12.8/B**, sete imagens verificadas antes da escrita e sete partições verificadas integralmente após a escrita. Manifesto idêntico ao [oficial comma/openpilot v0.10.0](https://github.com/commaai/openpilot/blob/v0.10.0/system/hardware/tici/agnos.json). Boot e retorno por SSH confirmados.
- Instalação completa prebuilt, origem N30-PH/FrogPilot, branch própria e versão-base exibida **0.10.3**. Código antigo preservado em outra pasta; nenhum reset de instalação/treinamento solicitado pelo procedimento.
- Aplicação Panda TRES atualizada uma vez, sem gravar bootloader. Binário distribuído: SHA256 `497d3625db564a31eada75f382da25eb2970069bc43cce74d4a6e82902eac708`. Assinatura de identificação relida por uma conexão independente e igual à esperada; isso não é uma certificação de segurança física.
- **8 verificações adicionais passaram no Python 3.12.3 nativo do Comma**, importando o matcher completo da candidata: correspondência exata única, prioridade do resultado exato e seis casos negativos de firmware inválido. Usam o mesmo fixture publicado; nenhuma ECU foi consultada em bancada.
- Observação inicial: UI, manager, hardwared e pandad em execução; nenhum processo que deveria rodar ausente, temperatura verde, Panda noOutput, sem ignição/controle/faults e contadores CAN zerados. Sem tráfego do carro, isso não valida comunicação em uso.
- Assistência e identificação forçada desligadas; cache de identificação desconsiderado para a primeira verificação. Atualizador bloqueado no inicializador para manter a revisão fixada.
- Corrigido apenas o formato do metadado InstallDate, preservando sua data/hora original sem inventar fuso. Nenhum ganho de torque, controle longitudinal ou centralização alterado.

O contador SPI cresceu durante a observação. O código correspondente ao firmware (`b5801ef9c2d5eb545a106ebd42b9579ab65d2fa1`) também conta consultas normais VERSION como erro; cinco leituras controladas acrescentaram exatamente uma unidade cada. Isso explica essas cinco unidades e **não demonstra a origem de todos os incrementos**. O contador isolado não foi convertido em diagnóstico de defeito nem em aprovação de comunicação.

O proprietário dispensou cópias adicionais de segurança durante a preparação. Artefatos já completos e a instalação antiga foram preservados, mas **não existe backup externo integral nem rollback físico ensaiado nesta execução**. Retorno de Git não restaura AGNOS/Panda. Nenhum dado pessoal bruto ou credencial é publicado.

**Próxima verificação:** veículo estacionado, assistência desligada, confirmar reconhecimento automático e preservar os logs de identificação/CAN/Panda. Não inferir segurança de condução somente do nome reconhecido.


## Base e alteração

Base fixada: [FrogPilot-Testing, 728f654727be9ecb71c16d95bd869ed051bb147f](https://github.com/FrogAi/FrogPilot/tree/728f654727be9ecb71c16d95bd869ed051bb147f).
Essa era a ponta pública de Testing consultada; **não é a release estável FrogPilot**. Não usar MAKE-PRS-HERE como instalação.

Testing já inclui HONDA_CITY_7G. A alteração funcional é exclusivamente acrescentar seis versões em `opendbc_repo/opendbc/car/honda/fingerprints.py`, preservando as entradas e os dois bytes nulos finais. Não altera consultas CAN, controlador, torque, calibração, longitudinal, safety, versões de sistema ou modelos.

| ECU no cadastro | Endereço | Firmware acrescentado |
|---|---|---|
| EPS | 0x18da30f1 | 39990-T14-B510 |
| Gateway | 0x18daeff1 | 38897-T14-M210 |
| SRS | 0x18da53f1 | 77959-T14-B810 |
| fwdRadar | 0x18dab0f1 | 8S102-T14-P020 |
| VSA | 0x18da28f1 | 57114-T14-M510 |
| Transmission | 0x18da1ef1 | 28101-63B-M510 |

fwdRadar é o identificador do banco, não afirma presença de radar físico. O nome exibido de 2023 foi preservado: esta candidata não amplia a alegação de compatibilidade para outras variantes.

Proveniência: [FrogPilot #322](https://github.com/FrogAi/FrogPilot/pull/322), [comma/opendbc #3812](https://github.com/commaai/opendbc/pull/3812). Créditos ao trabalho anterior de baninfelipe, commaai/opendbc#3340 e sunnypilot/opendbc#487. PR #322 foi incorporado em MAKE-PRS-HERE; isso não significa distribuição na release.

## Verificação executada

Windows/Python 3.12, numpy 2.3.5, pycapnp 2.1.0. Fontes obtidas pela revisão fixa, verificadas contra hashes de blobs da árvore GitHub. Catálogos, classes de veículos, schema e configurações de consulta importados da base real: **14 marcas / 216 plataformas**.

Cinco funções originais de matching foram selecionadas por AST e executadas sem modificar seu corpo; isso evita carregar o restante do runtime. **182 verificações aprovadas**, incluindo:
- baseline sem match exato; candidata com match exato único HONDA_CITY_7G;
- matching fuzzy genérico e preferência do combinado pelo resultado exato;
- 64 subconjuntos das adições: somente as seis juntas reconhecem exatamente este inventário completo;
- firmware desconhecido e ausência dos bytes finais rejeitados no matching exato;
- 64 subconjuntos do inventário e preservação dos catálogos Honda;
- respostas marcadas como logging excluídas do inventário de matching.

O fixture foi reconstruído dos seis pares endereço/versão publicados nos PRs. **Não é uma consulta nova às ECUs nem replay dos 17 registros privados originais.** Fuzzy pode aceitar dados incompletos conforme as regras inalteradas da base; não foi enfraquecido.

Blob do arquivo validado: `564c5b5740835f5cd054e2814a3d6d2914603596`.
SHA256: `9936d586b4e95c98e8972f940ff66e8edf5d4443d5ff369ea67a08c7062d7100`.
Detalhes em [validation.json](validation.json).

**Limites atuais:** runtime de bancada e metadados/assinatura Panda foram verificados após a instalação; CI Linux/ARM64 completa, nova compilação no Comma, resposta física EPS e teste no veículo não foram executados. Os fallbacks fuzzy específicos de todas as marcas não receberam uma suíte exaustiva. A primeira tentativa local faltava o módulo CAN do próprio catálogo Volkswagen; a dependência de fonte foi adicionada sem mudar o código funcional e a execução completa passou.

## Reproduzir no computador

Em ambiente Python 3.12 isolado, com numpy 2.3.5 e pycapnp 2.1.0 disponíveis:
```sh
python city2025/download_sources.py
python city2025/validate_candidate.py
```
Os scripts baixam somente as fontes selecionadas da base fixa e reproduzem a alteração em uma pasta de teste. O resultado deve ter o blob acima; não instalar a pasta de fontes reduzida. Não iniciar manager, launcher ou serviços do aparelho para executar esses testes.

## Troca sem reinstalar: avaliação e condições

É tecnicamente possível conservar a instalação/configuração e trocar para uma branch própria, **quando base, sistema, dependências, arquivos locais e fluxo de atualização forem reconciliados**. As condições do aparelho do proprietário foram auditadas e a instalação em bancada foi realizada conforme o registro acima. Isso não estabelece compatibilidade de outros aparelhos ou veículos.

A base Testing exige **AGNOS 12.8** em launch_env.sh. Seu launch_chffrplus.sh chama o atualizador de AGNOS se /VERSION for diferente e pode reiniciar. Portanto, trocar branch e reiniciar não é necessariamente uma operação apenas de código. O boot 12.8, os serviços em bancada e a Panda foram observados no comma 3X do proprietário. Condução e reconhecimento com ECUs reais continuam pendentes nesta candidata.

Antes de qualquer ativação:
1. Confirmar identidade SSH por canal confiável, hardware, /VERSION, slot, instalação efetiva, commit/branch/remotes, alterações e arquivos não rastreados.
2. Conferir dependências incorporadas, binários prebuilt, firmware Panda, atualizador e updates já preparados; não contornar a exigência de sistema.
3. Preservar o código atual, arquivos não rastreados necessários e parâmetros em área privada, com hashes e espaço disponível. Histórico de Git não salva parâmetros.
4. Preparar retorno para o commit exato anterior e remotos anteriores. Caso o AGNOS ou Panda mude, retorno de Git sozinho não restaura esses componentes.
5. Se a condição permitir mudança apenas de código, definir procedimento controlado, em bancada, mantendo recuperação disponível. Não usar checkout forçado, reset destrutivo, limpeza ou reinício automático por este documento.
6. Validar inicialização/UI/serviços em bancada; depois reconhecimento estacionado no veículo. Assistência de direção/frenagem exige avaliação separada.

**Não há comandos de instalação automática neste documento.** Publicação da candidata não é autorização técnica para condução. Nenhum ajuste de baixa velocidade ou de centralização faz parte deste patch.

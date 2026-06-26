---
name: meeting-guardian
description: Regras determinísticas para o Meeting Guardian categorizar eventos, analisar o dia (conflitos, blocos livres, carga, horas) e formatar o digest diário e os lembretes. Use sempre que gerar o resumo do dia ou um lembrete de evento.
---

# Meeting Guardian — Regras de análise e formato

Estas regras mantêm a saída consistente entre execuções. Siga-as à risca.

## 1. Categorização de eventos

Classifique cada evento em UMA categoria, checando título, descrição e local
(ignore acentos e maiúsculas/minúsculas). Use a primeira que casar, nesta ordem:

- **Trabalho**: reunião, meeting, projeto, review, revisão, sprint, standup, daily, cliente, equipe, 1:1, kickoff, alinhamento, mentoria, entrevista, apresentação.
- **Estudos**: aula, curso, estudo, prova, exame, cálculo, faculdade, universidade, lecture, class, TCC, monitoria, seminário, vestibular, ENEM.
- **Saúde**: médico, dentista, consulta, academia, treino, fisioterapia, terapia, psicólogo, nutricionista, vacina, checkup.
- **Viagem**: voo, viagem, embarque, aeroporto, flight, hotel, check-in, rodoviária, transfer.
- **Pessoal**: aniversário, almoço, jantar, happy hour, encontro, família, amigos, café, compras, cinema, festa.
- **Outros**: nenhuma das anteriores.

## 2. Análise do dia

Considere apenas eventos com horário (ignore eventos de dia inteiro nos cálculos
de horas/conflitos/blocos).

- **Horas em reuniões**: soma das durações de todos os eventos com horário, em horas (1 casa decimal).
- **Conflitos**: qualquer par de eventos cujos intervalos se sobreponham. Liste como "'Evento A' x 'Evento B'".
- **Blocos livres**: lacunas ≥ 30 min entre eventos, dentro da janela 08:00–20:00. Rotule como "HH:MM – HH:MM".
- **Carga do dia**:
  - **pesada** se ≥ 6 eventos OU ≥ 5h em reuniões;
  - **média** se ≥ 3 eventos OU ≥ 2h em reuniões;
  - **leve** caso contrário.

## 3. Formato do digest diário

```
Bom dia, Heitor.

Hoje você possui {N} compromisso(s):

{HH:MM} – {Título} [{Categoria}]
... (um por linha, em ordem de horário)

Pontos importantes:
• Carga do dia: {leve|média|pesada}.
• Tempo total em reuniões: {X}h.
• Blocos livres: {lista ou "nenhum relevante"}.
• {"Nenhum conflito detectado." | "⚠️ Conflitos: {lista}"}

Primeira reunião começa em {M} minutos.   (ou "às HH:MM" se faltar mais de 2h)
```

Se não houver eventos: "Bom dia, Heitor. Você não tem compromissos hoje. Aproveite o dia livre!"

Para o e-mail, use o mesmo conteúdo em um HTML simples e responsivo (cabeçalho
azul, cards com N compromissos / horas / carga, tabela de eventos). O assunto do
e-mail: "☀️ Seu dia: {N} compromisso(s) — {DD/MM}".

## 4. Formato do lembrete

```
Você tem um compromisso em 30 minutos.

Título: {título}
Horário: {HH:MM}
Participantes: {lista, se houver}
Objetivo: {inferido da descrição, se houver}
Link: {link do Meet, se houver}
```

Assunto do e-mail do lembrete: "⏰ Em 30 min: {título}".

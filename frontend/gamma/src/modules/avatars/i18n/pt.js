import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.avatars.heading.text',
    defaultMessage: 'Configurações de avatares',
    description: 'O texto exibido no cabeçalho da página de configurações de avatares.',
  },
  studentAvatarLockedTitle: {
    id: 'modules.avatars.student.avatar.locked.text',
    defaultMessage: 'Personagem bloqueado',
    description: 'O texto exibido no selo de um avatar bloqueado.',
  },
  pageDescription: {
    id: 'modules.avatars.page.description',
    defaultMessage: 'Esta página exibe medalhas e permite que os usuários as criem e editem.',
    description: 'A descrição da página de configurações de avatares.',
  },
  totalAvatarSetsCount: {
    id: 'modules.avatars.total-avatars-sets.counter.text',
    defaultMessage: 'Total de conjuntos de avatares: {avatarSetsCount}',
    description: 'O texto exibido para o número total de conjuntos de avatares.',
  },
  totalAvatarsCount: {
    id: 'modules.avatars.total-avatars.counter.text',
    defaultMessage: 'Total de avatares: {avatarsCount}',
    description: 'O texto exibido para o número total de avatares.',
  },
  addAvatarSetBtnText: {
    id: 'modules.avatars.button.add-avatar-set',
    defaultMessage: 'Adicionar conjunto de avatares',
    description: 'O texto exibido no botão para adicionar um novo conjunto de avatares.',
  },
  alertEmptyAvatarSetListTitle: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.title',
    defaultMessage: 'Nenhum conjunto de avatares disponível',
    description: 'O título do alerta quando não há conjuntos de avatares para exibir.',
  },
  alertEmptyAvatarsListTitle: {
    id: 'modules.avatars.avatars.alert.empty-avatars-list.title',
    defaultMessage: 'São necessários pelo menos dois estágios de avatar',
    description: 'O título do alerta quando não há avatares para exibir.',
  },
  alertEmptyAvatarSetListDescription: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.description',
    defaultMessage: 'Atualmente, não há conjuntos de avatares para exibir.',
    description: 'A descrição do alerta quando não há conjuntos de avatares para exibir.',
  },
  alertEmptyAvatarsListDescription: {
    id: 'modules.avatars.avatars.alert.empty-avatar-set-list.description',
    defaultMessage: 'Você pode adicionar predefinições de avatar na etapa anterior: Evolução.',
    description: 'A descrição do alerta quando não há avatares para exibir, mencionando que predefinições podem ser adicionadas na etapa anterior (Evolução).',
  },
  avatarSetEditBtnTitle: {
    id: 'modules.avatars.avatar-set.button.edit.title',
    defaultMessage: 'Editar',
    description: 'O texto exibido no botão para editar um conjunto de avatares.',
  },
  avatarEditBtnTitle: {
    id: 'modules.avatars.avatar.button.edit.title',
    defaultMessage: 'Editar',
    description: 'O texto exibido no botão para editar um avatar.',
  },
  avatarSetDeleteBtnTitle: {
    id: 'modules.avatars.avatar-set.button.delete.title',
    defaultMessage: 'Excluir',
    description: 'O texto exibido no botão para excluir um conjunto de avatares.',
  },
  avatarSetDraftBadgeText: {
    id: 'modules.avatars.avatar-set.draft.badge.text',
    defaultMessage: 'Rascunho',
    description: 'O texto exibido no selo de um conjunto de avatares com status de rascunho.',
  },
  avatarDeleteBtnTitle: {
    id: 'modules.avatars.avatar.button.delete.title',
    defaultMessage: 'Excluir',
    description: 'O texto exibido no botão para excluir um avatar.',
  },
  toastErrorTitle: {
    id: 'modules.avatars.toast.error.text',
    defaultMessage: 'Ocorreu um erro.',
    description: 'O texto exibido na mensagem de erro do toast.',
  },
  toastNewAvatarSetSavedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.saved.avatar-set.title',
    defaultMessage: 'Dados do conjunto de avatares salvos com sucesso',
    description: 'O título da mensagem toast quando os dados do conjunto de avatares são salvos com sucesso.',
  },
  toastAvatarSetDeletedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.deleted.avatar-set.title',
    defaultMessage: 'Conjunto de avatares excluído com sucesso',
    description: 'O título da mensagem toast quando um conjunto de avatares é excluído com sucesso.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.avatars.alert.modal.confirm.deletion.title',
    defaultMessage: 'Confirmar exclusão',
    description: 'O título do modal de confirmação ao excluir um conjunto de avatares.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.description',
    defaultMessage: 'Tem certeza de que deseja excluir este conjunto de avatares? Esta ação não pode ser desfeita.',
    description: 'A descrição do modal de confirmação ao excluir um conjunto de avatares.',
  },
  confirmAvatarStageDeletionModalTitle: {
    id: 'modules.avatars.alert.modal.confirm.deletion.avatar.stage.title',
    defaultMessage: 'Confirmar exclusão',
    description: 'The title for the confirmation modal when deleting a avatar stage.',
  },
  confirmAvatarStageDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.avatar.stage.description',
    defaultMessage: 'Tem certeza que deseja excluir este estágio do avatar? Esta ação não pode ser desfeita.',
    description: 'The description for the confirmation modal when deleting a avatar stage.',
  },
  confirmAvatarDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.avatar.description',
    defaultMessage: 'Tem certeza de que deseja excluir este avatar? Esta ação não pode ser desfeita.',
    description: 'A descrição do modal de confirmação ao excluir um avatar.',
  },
  editAvatarModalTitle: {
    id: 'modules.avatars.manage.modal.edit-avatar.title',
    defaultMessage: 'Editar avatar',
    description: 'O título do modal de edição de avatar.',
  },
  avatarSetStepperBtnStatefulDefaultText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.default.text',
    defaultMessage: 'Próximo',
    description: 'Texto para o estado padrão do botão com estado dentro do assistente de conjunto de avatares.',
  },
  avatarSetStepperBtnStatefulPendingText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.pending.text',
    defaultMessage: 'Salvando',
    description: 'Texto para o estado pendente do botão com estado dentro do assistente de conjunto de avatares.',
  },
  avatarSetStepperBtnStatefulCompleteText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.complete.text',
    defaultMessage: 'Salvo',
    description: 'Texto para o estado completo do botão com estado dentro do assistente de conjunto de avatares.',
  },
  avatarSetStepperBtnFinishText: {
    id: 'modules.avatars.avatar-set.stepper.button.finish.text',
    defaultMessage: 'Concluir',
    description: 'Texto do botão "concluir" dentro do assistente de conjunto de avatares.',
  },
  avatarSetStepperTitle: {
    id: 'modules.avatars.avatar-set.stepper.add-avatar-set.title',
    defaultMessage: 'Adicionar novo conjunto de avatares',
    description: 'Título do assistente para adicionar conjunto de avatares.',
  },
  avatarSetStepperEditTitle: {
    id: 'modules.avatars.avatar-set.stepper.edit-avatar-set.title',
    defaultMessage: 'Editar conjunto de avatares',
    description: 'Título do assistente para editar conjunto de avatares.',
  },
  avatarSetStepperValidationTitleRequired: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-required',
    defaultMessage: 'O título é obrigatório',
    description: 'Mensagem de validação para o campo de título no assistente.',
  },
  avatarSetStepperValidationTitleMaxLength: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-max-length',
    defaultMessage: 'O título deve ter no máximo 50 caracteres',
    description: 'Mensagem de validação quando o título excede 50 caracteres.',
  },
  avatarSetStepperValidationTitleLettersNumbers: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-letters-numbers',
    defaultMessage: 'O título deve conter apenas letras e números',
    description: 'Mensagem de validação quando o título contém caracteres inválidos.',
  },
  avatarSetStepperValidationTitleUnique: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-unique',
    defaultMessage: 'Este título já existe',
    description: 'Mensagem de validação quando o título já está em uso.',
  },
  avatarSetStepperCloseBtnTitle: {
    id: 'modules.avatars.avatar-set.stepper.button.close.title',
    defaultMessage: 'Fechar',
    description: 'Texto do botão "fechar" no assistente de conjunto de avatares.',
  },
  avatarSetStepperPreviousBtnTitle: {
    id: 'modules.avatars.avatar-set.stepper.button.previous.title',
    defaultMessage: 'Anterior',
    description: 'Texto do botão "anterior" no assistente de conjunto de avatares.',
  },
  avatarSetStepperFinishStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.finish.title',
    defaultMessage: 'Concluir',
    description: 'Título da etapa de conclusão no assistente de conjunto de avatares.',
  },
  avatarCardRuleSectionTitle: {
    id: 'modules.avatars.avatar-set.card.rule.subsection.title',
    defaultMessage: 'Regra {count}',
    description: 'Título da subseção de regras no cartão de avatar.',
  },
  avatarCardEventTypeFilterTitle: {
    id: 'modules.avatars.avatar-set.card.count.event-type.title',
    defaultMessage: 'Tipo de evento',
    description: 'Título do filtro de tipo de evento no cartão de avatar.',
  },
  avatarCardCountFilterTitle: {
    id: 'modules.avatars.avatar-set.card.count.filter.title',
    defaultMessage: 'Contagem',
    description: 'Título do filtro de contagem no cartão de avatar.',
  },
  avatarCardIntervalFilterTitle: {
    id: 'modules.avatars.avatar-set.card.interval.filter.title',
    defaultMessage: 'Intervalo',
    description: 'Título do filtro de intervalo no cartão de avatar.',
  },
  avatarCardFrequencyFilterTitle: {
    id: 'modules.avatars.avatar-set.card.frequency.filter.title',
    defaultMessage: 'Frequência',
    description: 'Título do filtro de frequência no cartão de avatar.',
  },
  avatarCardCourseFilterTitle: {
    id: 'modules.avatars.avatar-set.card.course.filter.title',
    defaultMessage: 'Curso',
    description: 'Título do filtro de curso no cartão de avatar.',
  },
  avatarCardOrganizationFilterTitle: {
    id: 'modules.avatars.avatar-set.card.organization.filter.title',
    defaultMessage: 'Organização',
    description: 'Título do filtro de organização no cartão de avatar.',
  },
  avatarSetStepperAvatarsStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.avatars.title',
    defaultMessage: 'Avatares',
    description: 'Título da etapa de avatares no assistente de conjunto de avatares.',
  },
  avatarSetStepperEvolutionStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.title',
    defaultMessage: 'Evolução',
    description: 'Título da etapa de evolução no assistente de conjunto de avatares.',
  },
  avatarSetStepperTitleStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.title.title',
    defaultMessage: 'Título',
    description: 'Título da etapa de título no assistente de conjunto de avatares.',
  },
  avatarSetStepperTitleStepDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.title.description',
    defaultMessage: 'Por favor, insira o título do conjunto de avatares abaixo.',
    description: 'Descrição da etapa de título no assistente.',
  },
  avatarSetStepperTitleStepInputTitleLabel: {
    id: 'modules.avatars.avatar-set.stepper.step.title.input.title.label',
    defaultMessage: 'Inserir título',
    description: 'Rótulo do campo de entrada de título na etapa de título do assistente.',
  },
  avatarSetStepperEvolutionAddStageBtn: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.button.add-stage.title',
    defaultMessage: 'Adicionar estágio de evolução',
    description: 'Título do botão para adicionar estágio de evolução na etapa de evolução.',
  },
  avatarSetStepperEvolutionDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.description.text',
    defaultMessage: `Faça o upload dos arquivos base para os estágios de evolução do avatar.
O número mínimo de estágios de evolução é 2, e o máximo é 5.
Certifique-se de que as imagens não incluam acessórios. Formato aceito: SVG.
Tamanho máximo do arquivo: 20 MB.`,
    description: 'Descrição da etapa de evolução no assistente de conjunto de avatares.',
  },
  avatarSetStepperEvolutionRemoveAvatarBtn: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.button.remove-avatar.text',
    defaultMessage: 'Remover',
    description: 'Texto do botão para remover avatar na etapa de evolução.',
  },
  avatarSetStepperEvolutionAvatarStageTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.stage.title',
    defaultMessage: 'Estágio {index}',
    description: 'Título do estágio do avatar na etapa de evolução.',
  },
  avatarSetStepperEvolutionAvatarDefaultTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.default.title',
    defaultMessage: 'Avatar {index}',
    description: 'Título padrão do avatar na etapa de evolução.',
  },
  avatarSetStepperEvolutionAvatarDefaultDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.default.description',
    defaultMessage: 'Alguma descrição para o avatar {index}',
    description: 'Descrição padrão do avatar na etapa de evolução.',
  },
});

export default messages;

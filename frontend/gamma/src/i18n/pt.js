import { defineMessages } from 'react-intl';

const messages = defineMessages({
  loaderScreenReaderText: {
    id: 'generic.loader.screenReader.text',
    defaultMessage: 'A carregar...',
    description: 'Texto para leitores de ecrã dentro do componente Loader.',
  },
  alertDangerTitle: {
    id: 'generic.alert.danger.title',
    defaultMessage: 'Ocorreu um erro',
    description: 'Título dentro do componente de alerta de perigo.',
  },
  alertDangerDescription: {
    id: 'generic.alert.danger.description',
    defaultMessage: 'Ocorreu um erro ao processar o seu pedido. Por favor, tente novamente mais tarde ou contacte o suporte se o problema persistir.',
    description: 'Descrição dentro do componente de alerta de perigo.',
  },
  alertBtnCloseTitle: {
    id: 'generic.alert.button.close.title',
    defaultMessage: 'Fechar',
    description: 'Título para o botão de fechar dentro do componente de alerta.',
  },
  modalDialogBtnCancelText: {
    id: 'generic.modal.dialog.button.cancel.text',
    defaultMessage: 'Cancelar',
    description: 'Texto para o botão de cancelar dentro da caixa de diálogo modal.',
  },
  modalDialogBtnSubmitText: {
    id: 'generic.modal.dialog.button.submit.text',
    defaultMessage: 'Submeter',
    description: 'Texto para o botão de submeter dentro da caixa de diálogo modal.',
  },
  alertBtnCancelText: {
    id: 'generic.modal.alert.button.cancel.text',
    defaultMessage: 'Cancelar',
    description: 'Texto para o botão de cancelar dentro do alerta modal.',
  },
  alertBtnDeleteText: {
    id: 'generic.modal.alert.button.delete.text',
    defaultMessage: 'Eliminar',
    description: 'Texto para o botão de eliminar dentro do alerta modal.',
  },
  headerBtnSingOutText: {
    id: 'generic.header.button.sing.out.text',
    defaultMessage: 'Terminar sessão',
    description: 'Texto para o botão de terminar sessão dentro do cabeçalho.',
  },
  headerLogoAltText: {
    id: 'generic.header.logo.alt.text',
    defaultMessage: 'Gamificação',
    description: 'Texto alternativo para o logótipo dentro do cabeçalho.',
  },
  'generic.footer.logo.alt.text': {
    id: 'generic.footer.logo.alt.text',
    defaultMessage: 'Gamificação',
    description: 'Texto alternativo para o logótipo dentro do rodapé.',
  },
  btnStatefulDefaultText: {
    id: 'generic.modal.alert.button.stateful.default.text',
    defaultMessage: 'Eliminar',
    description: 'Texto para o estado padrão do botão com estado dentro do alerta modal.',
  },
  btnStatefulPendingText: {
    id: 'generic.modal.alert.button.stateful.pending.text',
    defaultMessage: 'A eliminar',
    description: 'Texto para o estado pendente do botão com estado dentro do alerta modal.',
  },
  btnStatefulCompleteText: {
    id: 'generic.modal.alert.button.stateful.complete.text',
    defaultMessage: 'Eliminado',
    description: 'Texto para o estado completo do botão com estado dentro do alerta modal.',
  },
  btnStatefulErrorText: {
    id: 'generic.modal.alert.button.stateful.error.text',
    defaultMessage: 'Erro',
    description: 'Texto para o estado de erro do botão com estado dentro do alerta modal.',
  },
  modalDialogBtnStatefulDefaultText: {
    id: 'generic.modal.dialog.button.stateful.default.text',
    defaultMessage: 'Guardar',
    description: 'Texto para o estado padrão do botão com estado dentro da caixa de diálogo modal.',
  },
  modalDialogBtnStatefulPendingText: {
    id: 'generic.modal.dialog.button.stateful.pending.text',
    defaultMessage: 'A guardar',
    description: 'Texto para o estado pendente do botão com estado dentro da caixa de diálogo modal.',
  },
  modalDialogBtnStatefulCompleteText: {
    id: 'generic.modal.dialog.button.stateful.complete.text',
    defaultMessage: 'Guardado',
    description: 'Texto para o estado completo do botão com estado dentro da caixa de diálogo modal.',
  },
  modalDialogBtnStatefulErrorText: {
    id: 'generic.modal.dialog.button.stateful.error.text',
    defaultMessage: 'Erro',
    description: 'Texto para o estado de erro do botão com estado dentro da caixa de diálogo modal.',
  },
  modalEntityValidationTitleRequiredText: {
    id: 'generic.modal.entity.validation.title.required',
    defaultMessage: 'O título é obrigatório',
    description: 'Mensagem de validação quando o título está em falta.',
  },
  modalEntityValidationSlugRequiredText: {
    id: 'generic.modal.entity.validation.slug.required',
    defaultMessage: 'O slug é obrigatório',
    description: 'Mensagem de validação quando o slug está em falta.',
  },
  modalEntityValidationSlugInvalidText: {
    id: 'generic.modal.entity.validation.slug.invalid',
    defaultMessage: 'O slug só pode conter letras, números, sublinhados e hífens',
    description: 'Mensagem de validação quando o formato do slug está incorreto.',
  },
  modalEntityValidationDescriptionRequiredText: {
    id: 'generic.modal.entity.validation.description.required',
    defaultMessage: 'A descrição é obrigatória',
    description: 'Mensagem de validação quando a descrição está em falta.',
  },
  modalEntityValidationImageRequiredText: {
    id: 'generic.modal.entity.validation.image.required',
    defaultMessage: 'A imagem é obrigatória',
    description: 'Mensagem de validação quando uma imagem não é carregada.',
  },
  modalEntityValidationImageSizeText: {
    id: 'generic.modal.entity.validation.image.size',
    defaultMessage: 'O tamanho do ficheiro deve ser inferior a {maxSize}MB',
    description: 'Mensagem de validação quando uma imagem carregada excede o limite de tamanho de ficheiro.',
  },
  modalEntityImageHeadingText: {
    id: 'generic.modal.entity.image.heading',
    defaultMessage: 'Imagem',
    description: 'O cabeçalho para a secção de imagem da entidade no modal.',
  },
  modalEntityImageBtnUploadText: {
    id: 'generic.modal.entity.image.button.upload',
    defaultMessage: 'Carregar imagem',
    description: 'O texto exibido no botão para carregar uma imagem para a entidade.',
  },
  modalEntityImagePreviewText: {
    id: 'generic.modal.entity.image.preview.screenReader.text',
    defaultMessage: 'Pré-visualização da imagem',
    description: 'O texto para leitores de ecrã para a pré-visualização da imagem da entidade.',
  },
  modalEntityInfoHeadingText: {
    id: 'generic.modal.entity.information.heading',
    defaultMessage: 'Informações básicas',
    description: 'O cabeçalho para a secção de informações da entidade no modal.',
  },
  modalEntityInfoLabelEntityTitle: {
    id: 'generic.modal.entity.information.label.entity.title',
    defaultMessage: 'Título',
    description: 'O rótulo para o título da entidade no modal.',
  },
  modalEntityInfoLabelEntitySlugText: {
    id: 'generic.modal.entity.information.label.entity.slug',
    defaultMessage: 'Slug',
    description: 'Etiqueta para o slug da entidade no modal.',
  },
  modalEntityInfoLabelEntityDescriptionText: {
    id: 'generic.modal.entity.information.label.entity.description',
    defaultMessage: 'Descrição',
    description: 'Etiqueta para a descrição da entidade no modal.',
  },
  modalEntityInfoLabelEntityIsActiveText: {
    id: 'generic.modal.entity.is-active.text',
    defaultMessage: 'Ativo',
    description: 'Texto exibido para o estado ativo do distintivo.',
  },
  modalEntityInfoLabelEntityCategoryText: {
    id: 'generic.modal.entity.information.label.entity.category',
    defaultMessage: 'Categoria',
    description: 'O rótulo/marcador do campo de texto livre da categoria do distintivo, usado para agrupar e ordenar distintivos.',
  },
  modalEntityRulesTitle: {
    id: 'generic.modal.entity.rules.heading',
    defaultMessage: 'Regras',
    description: 'Título da seção de regras da entidade no modal.',
  },
  modalEntityRulesAddNewRuleBtnText: {
    id: 'generic.modal.entity.rules.button.add-new-rule.text',
    defaultMessage: 'Adicionar nova regra',
    description: 'Texto exibido no botão para adicionar uma nova regra.',
  },
  modalEntityRulesAlertNoRulesTitle: {
    id: 'generic.modal.entity.rules.alert.no-rules.heading',
    defaultMessage: 'Nenhuma regra disponível',
    description: 'Título do alerta quando não há regras a exibir.',
  },
  modalEntityRulesAlertNoRulesDescription: {
    id: 'generic.modal.entity.rules.alert.no-rules.description',
    defaultMessage: 'Ainda não adicionou nenhuma regra. Clique no botão abaixo para adicionar a sua primeira regra.',
    description: 'Descrição do alerta quando não há regras a exibir.',
  },
  modalEntityRulesRuleTitle: {
    id: 'generic.modal.entity.rules.rule.heading',
    defaultMessage: 'Regra {id}',
    description: 'Título de uma regra no modal.',
  },
  modalEntityRulesRuleEventTypeLabel: {
    id: 'generic.modal.entity.rules.rule.event-type.label',
    defaultMessage: 'Tipo de evento',
    description: 'Etiqueta para o tipo de evento da regra no modal.',
  },
  modalEntityRulesRuleCountLabel: {
    id: 'generic.modal.entity.rules.rule.count.label',
    defaultMessage: 'Contagem',
    description: 'Etiqueta para a contagem da regra no modal.',
  },
  modalEntityRulesRuleCourseLabel: {
    id: 'generic.modal.entity.rules.rule.course.label',
    defaultMessage: 'Curso',
    description: 'Etiqueta para o curso da regra no modal.',
  },
  modalEntityRulesBtnDeleteText: {
    id: 'generic.modal.entity.rules.button.delete.text',
    defaultMessage: 'Eliminar regra',
    description: 'Texto exibido no botão para eliminar uma regra.',
  },
  modalEntityRulesBtnRemoveFilterText: {
    id: 'generic.modal.entity.rules.button.remove-filter.text',
    defaultMessage: 'Remover',
    description: 'Texto exibido no botão para remover um filtro.',
  },
  modalEntityRulesIntervalStartLabelText: {
    id: 'generic.modal.entity.rules.interval.start.label.text',
    defaultMessage: 'Data de início',
    description: 'Etiqueta para o intervalo de data de início no modal.',
  },
  modalEntityRulesIntervalEndLabelText: {
    id: 'generic.modal.entity.rules.interval.end.label.text',
    defaultMessage: 'Data de fim',
    description: 'Etiqueta para o intervalo de data de fim no modal.',
  },
  modalEntityRulesActionHeadingTitle: {
    id: 'generic.modal.entity.rules.action.heading.text',
    defaultMessage: 'Ação',
    description: 'Título da seção de ações no modal.',
  },
  modalEntityRulesFiltersHeadingTitle: {
    id: 'generic.modal.entity.rules.filters.heading.text',
    defaultMessage: 'Filtros',
    description: 'Título da seção de filtros no modal.',
  },
  modalEntityRulesFiltersSelectTitle: {
    id: 'generic.modal.entity.rules.filters.select.title',
    defaultMessage: 'Selecionar filtro',
    description: 'Título para o filtro de seleção no modal.',
  },
  modalEntityRulesFilterSelectTitle: {
    id: 'generic.modal.entity.rules.filter.select.title',
    defaultMessage: 'Selecionar um(a) {filterName}',
    description: 'Título para o filtro de seleção no modal.',
  },
  modalEntityActionEventNameLabelText: {
    id: 'generic.modal.entity.action.event.name.label',
    defaultMessage: 'Selecionar um(a) {eventType}',
    description: 'Etiqueta para o nome do evento da ação no modal.',
  },
  modalEntityValidationActionEventNameRequiredText: {
    id: 'generic.modal.entity.action.event.name.validation.text',
    defaultMessage: 'Tipo de evento é obrigatório',
    description: 'Mensagem de validação quando o tipo de evento está em falta.',
  },
  modalEntityValidationActionRequiredText: {
    id: 'generic.modal.entity.action.validation.required.text',
    defaultMessage: 'Este campo é obrigatório',
    description: 'Mensagem de validação quando a ação está em falta.',
  },
  modalEntityValidationActionPositiveNumberText: {
    id: 'generic.modal.entity.action.validation.positive-number.text',
    defaultMessage: 'Este campo deve ser um número positivo',
    description: 'Mensagem de validação quando a ação não é um número positivo.',
  },
  modalEntityValidationActionNumberText: {
    id: 'generic.modal.entity.action.validation.number.text',
    defaultMessage: 'Este campo deve ser um número',
    description: 'Mensagem de validação quando a ação não é um número.',
  },
  modalEntityValidationStartDateRequiredText: {
    id: 'generic.modal.entity.interval.validation.start-date.required.text',
    defaultMessage: 'Data de início é obrigatória',
    description: 'Mensagem de validação quando a data de início está em falta.',
  },
  modalEntityValidationEndDateRequiredText: {
    id: 'generic.modal.entity.interval.validation.end-date.required.text',
    defaultMessage: 'Data de fim é obrigatória',
    description: 'Mensagem de validação quando a data de fim está em falta.',
  },
  modalEntityValidationFrequencyNumberText: {
    id: 'generic.modal.entity.frequency.validation.int.text',
    defaultMessage: 'Frequência deve ser um número',
    description: 'Mensagem de validação quando a frequência não é um número.',
  },
  modalEntityValidationFrequencyPositiveNumberText: {
    id: 'generic.modal.entity.frequency.validation.positive-int.text',
    defaultMessage: 'Frequência deve ser um número positivo',
    description: 'Mensagem de validação quando a frequência não é um número positivo.',
  },
  modalEntityValidationFiltersText: {
    id: 'generic.modal.entity.filters.validation.text',
    defaultMessage: 'é obrigatório',
    description: 'Mensagem de validação quando um filtro está em falta.',
  },
  modalEntityOrganizationFilterTitle: {
    id: 'generic.modal.entity.organization.filter.title',
    defaultMessage: 'Organização',
    description: 'Título para o filtro de organização no modal.',
  },
  modalEntityValidationTitleMaxLengthText: {
    id: 'generic.modal.entity.validation.title.max-length',
    defaultMessage: 'O título não deve exceder 100 caracteres.',
    description: 'Mensagem de validação quando o título excede o comprimento máximo permitido.',
  },
  modalEntityValidationSlugMaxLengthText: {
    id: 'generic.modal.entity.validation.slug.max-length',
    defaultMessage: 'O slug não deve exceder 30 caracteres.',
    description: 'Mensagem de validação quando o slug excede o comprimento máximo permitido.',
  },
  modalEntityValidationDescriptionMaxLengthText: {
    id: 'generic.modal.entity.validation.description.max-length',
    defaultMessage: 'A descrição não deve exceder 300 caracteres.',
    description: 'Mensagem de validação quando a descrição excede o comprimento máximo permitido.',
  },
  headerBadgesLinkText: {
    id: 'generic.header.nav.badges',
    defaultMessage: 'Conquistas',
    description: 'Texto exibido para o link de Distintivos no cabeçalho.',
  },
  headerAvatarsLinkText: {
    id: 'generic.header.nav.avatars',
    defaultMessage: 'Avatares',
    description: 'Texto exibido para o link de Avatares no cabeçalho.',
  },
  pgnDropzoneDefaultContentLabel: {
    id: 'pgn.Dropzone.DefaultContent.label',
    defaultMessage: 'Arraste e solte o seu ficheiro aqui ou clique para carregar.',
    description: 'Etiqueta de conteúdo padrão para o componente Dropzone.',
  },
  genericManageEntityModalEntityInfoTitle: {
    id: 'generic.manage.entity.modal.entity.info.title',
    defaultMessage: 'O título contém caracteres não suportados',
    description: 'A mensagem de validação para o campo de título no modal de gerenciamento de entidade.',
  },
});

export default messages;

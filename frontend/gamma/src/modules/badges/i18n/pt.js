import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.badges.heading.text',
    defaultMessage: 'Configurações de distintivos',
    description: 'O texto exibido no cabeçalho da página de configurações de distintivos.',
  },
  pageDescription: {
    id: 'modules.badges.page.description',
    defaultMessage: 'Esta página exibe os distintivos e permite que os usuários os criem e editem.',
    description: 'A descrição da página de configurações de distintivos.',
  },
  addBadgeBtnText: {
    id: 'modules.badges.button.add-badge',
    defaultMessage: 'Adicionar distintivo',
    description: 'O texto exibido no botão para adicionar um distintivo.',
  },
  totalBadgesCount: {
    id: 'modules.badges.total-badges.counter.text',
    defaultMessage: 'Total de distintivos: {badgesCount}',
    description: 'O texto exibido para o número total de distintivos.',
  },
  badgeEditBtnTitle: {
    id: 'modules.badges.badge-item.button.edit.title',
    defaultMessage: 'Editar',
    description: 'O texto exibido no botão para editar um distintivo.',
  },
  badgeDeleteBtnTitle: {
    id: 'modules.badges.badge-item.button.delete.title',
    defaultMessage: 'Excluir',
    description: 'O texto exibido no botão para excluir um distintivo.',
  },
  badgeDefaultTitle: {
    id: 'modules.badges.badge-item.default.title',
    defaultMessage: 'Título do distintivo',
    description: 'O título padrão de um distintivo.',
  },
  badgeDefaultDescription: {
    id: 'modules.badges.badge-item.default.description',
    defaultMessage: 'Descrição do distintivo',
    description: 'A descrição padrão de um distintivo.',
  },
  alertEmptyBadgesListTitle: {
    id: 'modules.badges.alert.empty-badges-list.title',
    defaultMessage: 'Nenhum distintivo disponível',
    description: 'O título do alerta quando não há distintivos para exibir.',
  },
  alertEmptyBadgesListDescription: {
    id: 'modules.badges.alert.empty-badges-list.description',
    defaultMessage: 'Atualmente, não há distintivos para exibir.',
    description: 'A descrição do alerta quando não há distintivos para exibir.',
  },
  addManageEntityModalTitle: {
    id: 'modules.badges.modal.add-badge.title',
    defaultMessage: 'Adicionar novo distintivo',
    description: 'O título do modal para adicionar distintivo.',
  },
  editManageEntityModalTitle: {
    id: 'modules.badges.modal.edit-badge.title',
    defaultMessage: 'Editar distintivo',
    description: 'O título do modal para editar distintivo.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.badges.alert.modal.confirm.deletion.title',
    defaultMessage: 'Confirmar exclusão',
    description: 'O título do modal de confirmação ao excluir um distintivo.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.badges.alert.modal.confirm.deletion.description',
    defaultMessage: 'Tem certeza de que deseja excluir este distintivo? Esta ação não pode ser desfeita.',
    description: 'A descrição do modal de confirmação ao excluir um distintivo.',
  },
  toastErrorTitle: {
    id: 'modules.badges.toast.error.text',
    defaultMessage: 'Ocorreu um erro.',
    description: 'O texto exibido na mensagem de erro do toast.',
  },
  badgeCreatedTitle: {
    id: 'modules.badges.alert.badge-created.title',
    defaultMessage: 'Distintivo criado com sucesso',
    description: 'O título do alerta quando um distintivo é criado com sucesso.',
  },
  badgeEditedTitle: {
    id: 'modules.badges.alert.badge-edited.title',
    defaultMessage: 'Distintivo editado com sucesso',
    description: 'O título do alerta quando um distintivo é editado com sucesso.',
  },
  badgeDeletedTitle: {
    id: 'modules.badges.alert.badge-deleted.title',
    defaultMessage: 'Distintivo excluído com sucesso',
    description: 'O título do alerta quando um distintivo é excluído com sucesso.',
  },
  badgeDraftStatusText: {
    id: 'modules.badges.badge.draft.status.text',
    defaultMessage: 'Rascunho',
    description: 'O texto exibido para o status de rascunho do distintivo.',
  },
  badgeActiveStatusText: {
    id: 'modules.badges.badge.active.status.text',
    defaultMessage: 'Ativo',
    description: 'O texto exibido para o status ativo do distintivo.',
  },
});

export default messages;
